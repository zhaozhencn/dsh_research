import { Service } from '@deepseek-ai/cordis'
import type { Context } from '@deepseek-ai/cordis'
import Schema from '@deepseek-ai/schemastery'
import type { Agent } from '@deepseek-ai/dsh-agent'
import { EnterpriseLedger } from './ledger.js'
import type { Subject, TaskSpec, Ticket } from './ledger.js'

declare module '@deepseek-ai/cordis' {
  interface Context { enterprisePlatform: EnterprisePlatform }
}

export interface Config { databasePath: string }

/** Local reference provider; deployment must protect the database and this process. */
export default class EnterprisePlatform extends Service {
  static inject = ['agents']
  static Config: Schema<Config> = Schema.object({ databasePath: Schema.string().required() })
  readonly ledger: EnterpriseLedger
  private readonly grants = new WeakMap<Agent, TaskSpec>()
  private readonly boundAgents = new Set<Agent>()
  private closing = false

  constructor(ctx: Context, config: Config) {
    super(ctx, 'enterprisePlatform')
    if (!config.databasePath.trim()) throw new Error('INVALID_DATABASE_PATH')
    this.ledger = new EnterpriseLedger(config.databasePath)
    ctx.effect(() => async () => {
      this.closing = true
      const agents = [...this.boundAgents]
      for (const agent of agents) agent.cancel({ kind: 'disposed' })
      await Promise.all(agents.map(agent => agent.whenIdle()))
      this.ledger.close()
    })
  }

  bind(owner: Context, agent: Agent, subject: Subject, taskId: string): TaskSpec {
    if (this.closing || this.grants.has(agent)) throw new Error('AGENT_BINDING_UNAVAILABLE')
    const grant = this.ledger.authorize(subject, taskId, agent.id)
    this.grants.set(agent, grant)
    this.boundAgents.add(agent)
    owner.effect(() => () => { this.grants.delete(agent); this.boundAgents.delete(agent) })
    return grant
  }

  /** Agent object identity matters; a reused session id does not restore a grant. */
  current(agent: Agent | undefined): TaskSpec {
    if (this.closing || !agent || this.ctx.agents.get(agent.id) !== agent) throw new Error('UNBOUND_AGENT')
    const grant = this.grants.get(agent)
    if (!grant) throw new Error('UNBOUND_AGENT')
    this.ledger.assertCurrent(grant)
    return grant
  }

  async readTicket(grant: TaskSpec, ticketId: string, signal: AbortSignal): Promise<Ticket> {
    signal.throwIfAborted()
    // Replace this boundary with a tenant-authorized backend connector in production.
    await Promise.resolve()
    signal.throwIfAborted()
    return this.ledger.readTicket(grant, ticketId)
  }

  observeFinal(agent: Agent, facts: object): void {
    // Revocation forbids data access, but must not erase the operation's audit identity.
    const grant = this.grants.get(agent)
    if (grant) this.ledger.audit(grant, 'tool-final-observed', facts)
  }
}
