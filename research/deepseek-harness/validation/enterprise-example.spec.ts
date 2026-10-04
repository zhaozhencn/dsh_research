import { describe, expect, it, vi } from 'vitest'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { DatabaseSync } from 'node:sqlite'
import { SessionId } from '@deepseek-ai/dsh-session'
import { createUserMessage, ToolCallId } from '@deepseek-ai/dsh-llm'
import type { StreamChunk } from '@deepseek-ai/dsh-llm'
import { defineTool } from '@deepseek-ai/dsh-tools'
import EnterprisePlatform from '../examples/enterprise-harness/lib/platform.js'
import { EnterpriseLedger } from '../examples/enterprise-harness/lib/ledger.js'
import { createEnterpriseAgent } from '../examples/enterprise-harness/lib/provision.js'
import { runtime, ScriptAdapter, send, text } from './mock-runtime.ts'

const subject = { tenantId: 'tenant-a', actorId: 'alice' }
const other = { tenantId: 'tenant-b', actorId: 'bob' }
function spec(taskId = 'task-a', actor = subject, maxAttempts = 4) {
  return { ...actor, taskId, sessionId: `session-${taskId}`, policyRevision: 1,
    provider: 'mock', model: 'enterprise', maxAttempts, maxTokens: 1024,
    expiresAt: Date.now() + 60_000, ticketId: 'T-42', expectedVersion: 1, canClose: true }
}
function call(name: string, args: object): StreamChunk[] {
  const id = ToolCallId(`enterprise-call-${name}`), json = JSON.stringify(args)
  return [
    { type: 'block-start', index: 0, blockType: 'tool-call' },
    { type: 'tool-call-delta', index: 0, id, name, argumentsDelta: json },
    { type: 'block-end', index: 0, block: { type: 'tool-call', id, name, arguments: json } },
    { type: 'finish', reason: { kind: 'tool-calls' } },
  ]
}
async function fixture(script: (StreamChunk[] | 'hang')[], body: (ctx: Awaited<ReturnType<typeof runtime>>, adapter: ScriptAdapter) => Promise<void>) {
  const adapter = new ScriptAdapter(script), ctx = await runtime(adapter)
  try {
    await ctx.plugin(EnterprisePlatform, { databasePath: ':memory:' })
    ctx.enterprisePlatform.ledger.putTicket(subject.tenantId, { ticketId: 'T-42', title: 'A-visible', status: 'open', version: 1 })
    ctx.enterprisePlatform.ledger.putTicket(other.tenantId, { ticketId: 'T-42', title: 'B-confidential', status: 'open', version: 1 })
    await body(ctx, adapter)
  } finally { await ctx.fiber.dispose() }
}
async function create(ctx: Awaited<ReturnType<typeof runtime>>, task = spec()) {
  ctx.enterprisePlatform.ledger.createTask(task)
  return createEnterpriseAgent(ctx, task, task.taskId, task.sessionId)
}
function latestTool(agent: { session: { snapshotEvents(): readonly { type: string }[] } }) {
  return agent.session.snapshotEvents().filter(event => event.type === 'tool/result').at(-1)
}
function nextChunk(ctx: Awaited<ReturnType<typeof runtime>>): Promise<void> {
  return new Promise(resolve => {
    const off = ctx.on('agent/assistant-stream', ({ frame }) => {
      if (frame.type === 'chunk' && frame.chunk.type === 'text-delta') { off(); resolve() }
    })
  })
}

describe('enterprise DSH extensions: real Loop, compiled plugins, local SQLite', () => {
  it('routes, caps output and returns only the bound tenant ticket into the next request', async () => {
    await fixture([call('enterprise_ticket_read', { ticketId: 'T-42' }), text('T-42 version 1')], async (ctx, adapter) => {
      const handle = await create(ctx)
      await send(handle.agent, '读取工单')
      expect(adapter.requests.map(r => r.model)).toEqual(['enterprise', 'enterprise'])
      expect(adapter.requests.every(r => r.maxTokens === 1024)).toBe(true)
      const messages = JSON.stringify(adapter.requests[1]?.messages)
      expect(messages).toContain('A-visible'); expect(messages).not.toContain('B-confidential')
      expect(ctx.enterprisePlatform.ledger.used('task-a')).toBe(2)
      expect(ctx.enterprisePlatform.ledger.auditPhases('task-a')).toEqual([
        'model-reserved', 'tool-dispatch-intent', 'tool-body-settled', 'tool-final-observed', 'model-reserved',
      ])
      await handle.dispose()
    })
  })
  it('separates identical ticket ids for different bound subjects and scopes', async () => {
    await fixture([call('enterprise_ticket_read', { ticketId: 'T-42' }), text('A'), call('enterprise_ticket_read', { ticketId: 'T-42' }), text('B')], async (ctx, adapter) => {
      const a = await create(ctx), b = await create(ctx, spec('task-b', other))
      await send(a.agent, 'A'); await send(b.agent, 'B')
      expect(JSON.stringify(adapter.requests[1]?.messages)).toContain('A-visible')
      expect(JSON.stringify(adapter.requests[1]?.messages)).not.toContain('B-confidential')
      expect(JSON.stringify(adapter.requests[3]?.messages)).toContain('B-confidential')
      expect(JSON.stringify(adapter.requests[3]?.messages)).not.toContain('A-visible')
      expect(ctx.tools.get('enterprise_ticket_read')).toBeUndefined()
      await a.dispose(); await b.dispose()
    })
  })
  it('rejects a forged subject before publishing an Agent or Session', async () => {
    await fixture([], async ctx => {
      const task = spec(); ctx.enterprisePlatform.ledger.createTask(task)
      await expect(createEnterpriseAgent(ctx, other, task.taskId, task.sessionId)).rejects.toThrow('NOT_AUTHORIZED')
      expect(ctx.agents.get(SessionId(task.sessionId))).toBeUndefined()
      expect(ctx.sessions.get(SessionId(task.sessionId))).toBeUndefined()
    })
  })
  it('does not grant access when the model supplies another tenant in tool arguments', async () => {
    await fixture([call('enterprise_ticket_read', { ticketId: 'T-42', tenantId: other.tenantId }), text('done')], async (ctx, adapter) => {
      const handle = await create(ctx); await send(handle.agent, 'try tenant parameter')
      // Whether extra fields are rejected or ignored, tenant selection stays server-bound.
      expect(JSON.stringify(adapter.requests[1]?.messages)).not.toContain('B-confidential')
      await handle.dispose()
    })
  })
  it('denies another resource even when it belongs to the same tenant', async () => {
    await fixture([call('enterprise_ticket_read', { ticketId: 'T-99' }), text('denied')], async ctx => {
      ctx.enterprisePlatform.ledger.putTicket(subject.tenantId, { ticketId: 'T-99', title: 'A-other-secret', status: 'open', version: 1 })
      const handle = await create(ctx); await send(handle.agent, 'try another ticket')
      expect(JSON.stringify(latestTool(handle.agent))).toContain('RESOURCE_NOT_AUTHORIZED')
      expect(JSON.stringify(handle.agent.session.snapshotEvents())).not.toContain('A-other-secret')
      await handle.dispose()
    })
  })
  it('uses a monotonic guard to deny extra scope-local tools that restrict cannot hide', async () => {
    await fixture([call('rogue_write', {}), text('denied')], async ctx => {
      const handle = await create(ctx), body = vi.fn(() => 1)
      handle.agent.ctx.tools.register(defineTool({ name: 'rogue_write', description: 'test-only', parameters: {},
        output: { schema: { type: 'number' }, render: (_args, value) => [{ type: 'text', text: String(value) }] }, execute: body }))
      await send(handle.agent, 'try extra tool')
      expect(body).not.toHaveBeenCalled()
      expect(JSON.stringify(latestTool(handle.agent))).toContain('TOOL_NOT_AUTHORIZED')
      await handle.dispose()
    })
  })
  it('rejects the next model attempt after the durable budget is exhausted', async () => {
    await fixture([call('enterprise_ticket_read', { ticketId: 'T-42' }), text('must not run')], async (ctx, adapter) => {
      const handle = await create(ctx, spec('limited', subject, 1)); await send(handle.agent, 'read')
      expect(adapter.requests).toHaveLength(1)
      expect(ctx.enterprisePlatform.ledger.used('limited')).toBe(1)
      expect(handle.agent.session.snapshotEvents().at(-1)).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'error' } } })
      await handle.dispose()
    })
  })
  it('rechecks authorization after downstream request hooks without consuming a reservation', async () => {
    await fixture([text('must not run')], async (ctx, adapter) => {
      const handle = await create(ctx)
      handle.agent.ctx.on('agent/request', async (_event, next) => {
        const config = await next(); ctx.enterprisePlatform.ledger.revoke(subject, 'task-a'); return config
      })
      await send(handle.agent, 'revoked during await')
      expect(adapter.requests).toHaveLength(0)
      expect(ctx.enterprisePlatform.ledger.used('task-a')).toBe(0)
      await handle.dispose()
    })
  })
  it('counts retry attempts inside one Step and terminates even when recovery keeps requesting retry', async () => {
    const failure: StreamChunk[] = [{ type: 'finish', reason: { kind: 'error', failure: {
      code: 'RATE_LIMITED', message: 'controlled failure',
    } } }]
    await fixture([failure, failure, text('must not run')], async (ctx, adapter) => {
      const handle = await create(ctx, spec('retry-limit', subject, 2))
      handle.agent.ctx.on('agent/request-error', async () => ({ kind: 'retry' }))
      await send(handle.agent, 'retry until bounded')
      expect(adapter.requests).toHaveLength(2)
      expect(ctx.enterprisePlatform.ledger.used('retry-limit')).toBe(2)
      expect(handle.agent.session.snapshotEvents().filter(e => e.type === 'step/start')).toHaveLength(1)
      expect(handle.agent.session.snapshotEvents().at(-1)).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'error' } } })
      await handle.dispose()
    })
  })
  it('rejects step admission when authorization is revoked inside the admission waterfall', async () => {
    await fixture([], async (ctx, adapter) => {
      const handle = await create(ctx)
      handle.agent.ctx.on('agent/pre-step', async (_event, next) => {
        const decision = await next(); ctx.enterprisePlatform.ledger.revoke(subject, 'task-a'); return decision
      })
      await send(handle.agent, 'revoked before step')
      expect(adapter.requests).toHaveLength(0)
      expect(handle.agent.session.snapshotEvents().filter(e => e.type === 'step/start')).toHaveLength(0)
      expect(handle.agent.session.snapshotEvents().at(-1)).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'blocked' } } })
      await handle.dispose()
    })
  })
  it('does not release a backend result if authorization changes during the await', async () => {
    await fixture([call('enterprise_ticket_read', { ticketId: 'T-42' })], async ctx => {
      const handle = await create(ctx)
      vi.spyOn(ctx.enterprisePlatform, 'readTicket').mockImplementation(async () => {
        ctx.enterprisePlatform.ledger.revoke(subject, 'task-a')
        return { ticketId: 'T-42', title: 'must-not-be-released', status: 'open', version: 1 }
      })
      await send(handle.agent, 'read and revoke')
      expect(JSON.stringify(latestTool(handle.agent))).toContain('AUTHORIZATION_EXPIRED_OR_REVOKED')
      expect(JSON.stringify(handle.agent.session.snapshotEvents())).not.toContain('must-not-be-released')
      await handle.dispose()
    })
  })
  it('propagates cancellation to the model and removes registrations at handle disposal', async () => {
    await fixture(['hang'], async ctx => {
      const handle = await create(ctx), partial = nextChunk(ctx)
      handle.agent.followup(createUserMessage({ content: [{ type: 'text', text: 'cancel' }], source: { kind: 'user' } }))
      await partial; handle.agent.cancel({ kind: 'user' }); await handle.agent.whenIdle()
      expect(handle.agent.session.snapshotEvents().at(-1)).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'aborted' } } })
      await handle.dispose()
      expect(ctx.agents.get(handle.agent.id)).toBeUndefined()
      expect(() => ctx.enterprisePlatform.current(handle.agent)).toThrow('UNBOUND_AGENT')
    })
  })
  it('cancels an active stream at the task deadline with an explicit hook cause', async () => {
    await fixture(['hang'], async ctx => {
      const task = { ...spec('deadline'), expiresAt: Date.now() + 500 }
      const handle = await create(ctx, task), partial = nextChunk(ctx)
      handle.agent.followup(createUserMessage({ content: [{ type: 'text', text: 'wait' }], source: { kind: 'user' } }))
      await partial; await handle.agent.whenIdle()
      const ending = handle.agent.session.snapshotEvents().at(-1)
      expect(ending).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'aborted' } } })
      expect(JSON.stringify(ending)).toContain('enterprise-task-deadline')
      await handle.dispose()
    })
  })
})

describe('application ledger: real local transactions, not remote exactly-once', () => {
  it('shares and preserves reservations across two connections and database reopening', async () => {
    const dir = await mkdtemp(join(tmpdir(), 'enterprise-ledger-')), file = join(dir, 'state.db')
    let a: EnterpriseLedger | undefined, b: EnterpriseLedger | undefined
    try {
      a = new EnterpriseLedger(file); b = new EnterpriseLedger(file)
      const task = spec('shared', subject, 2); a.createTask(task)
      a.reserveAttempt(task); b.reserveAttempt(task)
      expect(() => a!.reserveAttempt(task)).toThrow('MODEL_ATTEMPT_BUDGET_EXHAUSTED')
      a.close(); a = undefined; b.close(); b = undefined
      a = new EnterpriseLedger(file)
      expect(a.used('shared')).toBe(2)
      expect(() => a!.reserveAttempt(task)).toThrow('MODEL_ATTEMPT_BUDGET_EXHAUSTED')
      expect(a.auditPhases('shared')).toEqual(['model-reserved', 'model-reserved'])
    } finally { a?.close(); b?.close(); await rm(dir, { recursive: true, force: true }) }
  })
  it('commits business effect, idempotency receipt and audit together and returns the same receipt on retry', async () => {
    const dir = await mkdtemp(join(tmpdir(), 'enterprise-transaction-')), file = join(dir, 'state.db')
    const ledger = new EnterpriseLedger(file), injected = new DatabaseSync(file), task = spec('write')
    try {
      ledger.createTask(task); ledger.putTicket(subject.tenantId, { ticketId: 'T-42', title: 'ticket', status: 'open', version: 1 })
      // An actual database failure AFTER business UPDATE and receipt INSERT must roll both back.
      injected.exec(`CREATE TRIGGER reject_audit BEFORE INSERT ON audit
        WHEN NEW.phase='business-committed' BEGIN SELECT RAISE(ABORT,'audit unavailable'); END;`)
      expect(() => ledger.closeTicket(task)).toThrow('audit unavailable')
      expect(ledger.readTicket(task, 'T-42')).toMatchObject({ status: 'open', version: 1 })
      expect(ledger.auditPhases('write')).toEqual([])
      injected.exec('DROP TRIGGER reject_audit')
      const first = ledger.closeTicket(task), retry = ledger.closeTicket(task)
      expect(first).toEqual(retry)
      expect(ledger.readTicket(task, 'T-42')).toMatchObject({ status: 'closed', version: 2 })
      expect(ledger.auditPhases('write')).toEqual(['business-committed'])
      ledger.revoke(subject, 'write')
      expect(() => ledger.closeTicket(task)).toThrow('AUTHORIZATION_EXPIRED_OR_REVOKED')
    } finally { injected.close(); ledger.close(); await rm(dir, { recursive: true, force: true }) }
  })
  it('refuses writes without permission and rolls back a stale business version', () => {
    const ledger = new EnterpriseLedger(':memory:'), noWrite = { ...spec('read-only'), canClose: false }, stale = spec('stale')
    try {
      ledger.createTask(noWrite); ledger.createTask(stale)
      ledger.putTicket(subject.tenantId, { ticketId: 'T-42', title: 'newer', status: 'open', version: 2 })
      expect(() => ledger.closeTicket(noWrite)).toThrow('WRITE_NOT_AUTHORIZED')
      expect(() => ledger.closeTicket(stale)).toThrow('BUSINESS_VERSION_CONFLICT')
      expect(ledger.readTicket(stale, 'T-42')).toMatchObject({ status: 'open', version: 2 })
      expect(ledger.auditPhases('stale')).toEqual([])
    } finally { ledger.close() }
  })
})
