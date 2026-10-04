import { DatabaseSync } from 'node:sqlite'
import { createHash } from 'node:crypto'

export interface Subject { readonly tenantId: string; readonly actorId: string }
export interface TaskSpec extends Subject {
  readonly taskId: string
  readonly sessionId: string
  readonly policyRevision: number
  readonly provider: string
  readonly model: string
  readonly maxAttempts: number
  readonly maxTokens: number
  readonly expiresAt: number
  readonly ticketId: string
  readonly expectedVersion: number
  readonly canClose: boolean
}
export interface Ticket { ticketId: string; title: string; status: string; version: number }
export interface CloseReceipt { operationId: string; ticketId: string; status: string; version: number }

/** Application ledger, NOT a replacement for DSH SessionPersistence. */
export class EnterpriseLedger {
  private readonly db: DatabaseSync
  constructor(filename: string) {
    this.db = new DatabaseSync(filename)
    this.db.exec(`
      PRAGMA journal_mode=WAL;
      PRAGMA synchronous=FULL;
      PRAGMA busy_timeout=1000;
      CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY, session_id TEXT UNIQUE NOT NULL,
        tenant_id TEXT NOT NULL, actor_id TEXT NOT NULL, revision INTEGER NOT NULL,
        spec TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
        used INTEGER NOT NULL DEFAULT 0, limit_count INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
      );
      CREATE TABLE IF NOT EXISTS tickets (
        tenant_id TEXT NOT NULL, ticket_id TEXT NOT NULL, title TEXT NOT NULL,
        status TEXT NOT NULL, version INTEGER NOT NULL,
        PRIMARY KEY (tenant_id, ticket_id)
      );
      CREATE TABLE IF NOT EXISTS audit (
        seq INTEGER PRIMARY KEY, task_id TEXT NOT NULL, tenant_id TEXT NOT NULL,
        actor_id TEXT NOT NULL, session_id TEXT NOT NULL, phase TEXT NOT NULL,
        facts TEXT NOT NULL, recorded_at INTEGER NOT NULL
      );
      CREATE TABLE IF NOT EXISTS operations (
        tenant_id TEXT NOT NULL, operation_id TEXT NOT NULL,
        input_hash TEXT NOT NULL, receipt TEXT NOT NULL,
        PRIMARY KEY (tenant_id, operation_id)
      );
    `)
  }

  /** Called only by an authenticated, authorized application control plane. */
  createTask(spec: TaskSpec): void {
    for (const value of [spec.taskId, spec.sessionId, spec.tenantId, spec.actorId,
      spec.provider, spec.model, spec.ticketId]) {
      if (typeof value !== 'string' || !value.trim()) throw new Error('INVALID_TASK')
    }
    for (const value of [spec.policyRevision, spec.maxAttempts, spec.maxTokens,
      spec.expiresAt, spec.expectedVersion]) {
      if (!Number.isSafeInteger(value) || value <= 0) throw new Error('INVALID_TASK')
    }
    if (spec.expiresAt <= Date.now() || spec.expiresAt - Date.now() > 86_400_000
      || typeof spec.canClose !== 'boolean') throw new Error('INVALID_TASK')
    this.db.prepare(`INSERT INTO tasks
      (task_id,session_id,tenant_id,actor_id,revision,spec,limit_count,expires_at)
      VALUES (?,?,?,?,?,?,?,?)`).run(spec.taskId, spec.sessionId, spec.tenantId,
      spec.actorId, spec.policyRevision, JSON.stringify(spec), spec.maxAttempts, spec.expiresAt)
  }

  authorize(subject: Subject, taskId: string, sessionId: string): TaskSpec {
    const row = this.db.prepare(`SELECT spec FROM tasks WHERE task_id=? AND
      session_id=? AND tenant_id=? AND actor_id=? AND active=1 AND expires_at>?`)
      .get(taskId, sessionId, subject.tenantId, subject.actorId, Date.now())
    if (typeof row?.spec !== 'string') throw new Error('NOT_AUTHORIZED')
    // Written only by createTask(); this DB is inside the trusted control plane.
    const spec = JSON.parse(row.spec) as TaskSpec
    return Object.freeze(spec)
  }

  assertCurrent(spec: TaskSpec): void {
    const row = this.db.prepare(`SELECT spec FROM tasks WHERE task_id=? AND
      session_id=? AND tenant_id=? AND actor_id=? AND revision=? AND active=1 AND expires_at>?`)
      .get(spec.taskId, spec.sessionId, spec.tenantId, spec.actorId, spec.policyRevision, Date.now())
    if (!row || row.spec !== JSON.stringify(spec)) throw new Error('AUTHORIZATION_EXPIRED_OR_REVOKED')
  }

  /** Conservative reservation: failed preparation still consumes a slot. */
  reserveAttempt(spec: TaskSpec): void {
    this.transaction(() => {
      this.assertCurrent(spec)
      const changed = this.db.prepare(`UPDATE tasks SET used=used+1
        WHERE task_id=? AND used<limit_count AND active=1 AND revision=? AND expires_at>?`)
        .run(spec.taskId, spec.policyRevision, Date.now()).changes
      if (Number(changed) !== 1) throw new Error('MODEL_ATTEMPT_BUDGET_EXHAUSTED')
      this.audit(spec, 'model-reserved', { provider: spec.provider, model: spec.model })
    })
  }

  used(taskId: string): number {
    return Number(this.db.prepare('SELECT used FROM tasks WHERE task_id=?').get(taskId)?.used ?? 0)
  }

  revoke(subject: Subject, taskId: string): void {
    const changed = this.db.prepare(`UPDATE tasks SET active=0,revision=revision+1
      WHERE task_id=? AND tenant_id=? AND actor_id=?`)
      .run(taskId, subject.tenantId, subject.actorId).changes
    if (Number(changed) !== 1) throw new Error('NOT_AUTHORIZED')
  }

  /** Fixture/import API. Never expose this method as an Agent tool. */
  putTicket(tenantId: string, ticket: Ticket): void {
    this.db.prepare(`INSERT INTO tickets VALUES (?,?,?,?,?)
      ON CONFLICT(tenant_id,ticket_id) DO UPDATE SET
      title=excluded.title,status=excluded.status,version=excluded.version`)
      .run(tenantId, ticket.ticketId, ticket.title, ticket.status, ticket.version)
  }

  readTicket(spec: TaskSpec, ticketId: string): Ticket {
    this.assertCurrent(spec)
    if (ticketId !== spec.ticketId) throw new Error('RESOURCE_NOT_AUTHORIZED')
    const row = this.db.prepare(`SELECT ticket_id,title,status,version FROM tickets
      WHERE tenant_id=? AND ticket_id=?`).get(spec.tenantId, ticketId)
    if (!row) throw new Error('RESOURCE_UNAVAILABLE')
    if (typeof row.title !== 'string' || typeof row.status !== 'string') throw new Error('INVALID_RECORD')
    return { ticketId, title: row.title.slice(0, 200), status: row.status, version: Number(row.version) }
  }

  /** Trusted application command. Not registered as a model-visible tool. */
  closeTicket(spec: TaskSpec): CloseReceipt {
    return this.transaction(() => {
      this.assertCurrent(spec)
      if (!spec.canClose) throw new Error('WRITE_NOT_AUTHORIZED')
      const operationId = `${spec.taskId}:close-ticket`
      // Fixed field order; no model-supplied idempotency key or tenant.
      const inputHash = createHash('sha256').update(JSON.stringify([
        spec.tenantId, spec.actorId, spec.ticketId, spec.expectedVersion, 'closed',
      ])).digest('hex')
      const existing = this.db.prepare(`SELECT input_hash,receipt FROM operations
        WHERE tenant_id=? AND operation_id=?`).get(spec.tenantId, operationId)
      if (existing) {
        if (existing.input_hash !== inputHash || typeof existing.receipt !== 'string') {
          throw new Error('IDEMPOTENCY_CONFLICT')
        }
        return JSON.parse(existing.receipt) as CloseReceipt
      }
      const changed = this.db.prepare(`UPDATE tickets SET status='closed',version=version+1
        WHERE tenant_id=? AND ticket_id=? AND version=? AND status<>'closed'`)
        .run(spec.tenantId, spec.ticketId, spec.expectedVersion).changes
      if (Number(changed) !== 1) throw new Error('BUSINESS_VERSION_CONFLICT')
      const receipt: CloseReceipt = {
        operationId, ticketId: spec.ticketId, status: 'closed', version: spec.expectedVersion + 1,
      }
      this.db.prepare('INSERT INTO operations VALUES (?,?,?,?)')
        .run(spec.tenantId, operationId, inputHash, JSON.stringify(receipt))
      this.audit(spec, 'business-committed', receipt)
      return receipt
    })
  }

  /** Do not pass prompt bodies, ticket text, credentials or raw tool arguments. */
  audit(spec: TaskSpec, phase: string, facts: object): void {
    this.db.prepare(`INSERT INTO audit
      (task_id,tenant_id,actor_id,session_id,phase,facts,recorded_at) VALUES (?,?,?,?,?,?,?)`)
      .run(spec.taskId, spec.tenantId, spec.actorId, spec.sessionId, phase, JSON.stringify(facts), Date.now())
  }

  auditPhases(taskId: string): string[] {
    return this.db.prepare('SELECT phase FROM audit WHERE task_id=? ORDER BY seq')
      .all(taskId).map(row => String(row.phase))
  }

  close(): void { this.db.close() }

  private transaction<T>(body: () => T): T {
    this.db.exec('BEGIN IMMEDIATE')
    try {
      const value = body()
      this.db.exec('COMMIT')
      return value
    } catch (error) {
      this.db.exec('ROLLBACK')
      throw error
    }
  }
}
