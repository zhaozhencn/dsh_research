import { Service } from '@deepseek-ai/cordis';
import Schema from '@deepseek-ai/schemastery';
import { EnterpriseLedger } from './ledger.js';
/** Local reference provider; deployment must protect the database and this process. */
export default class EnterprisePlatform extends Service {
    static inject = ['agents'];
    static Config = Schema.object({ databasePath: Schema.string().required() });
    ledger;
    grants = new WeakMap();
    boundAgents = new Set();
    closing = false;
    constructor(ctx, config) {
        super(ctx, 'enterprisePlatform');
        if (!config.databasePath.trim())
            throw new Error('INVALID_DATABASE_PATH');
        this.ledger = new EnterpriseLedger(config.databasePath);
        ctx.effect(() => async () => {
            this.closing = true;
            const agents = [...this.boundAgents];
            for (const agent of agents)
                agent.cancel({ kind: 'disposed' });
            await Promise.all(agents.map(agent => agent.whenIdle()));
            this.ledger.close();
        });
    }
    bind(owner, agent, subject, taskId) {
        if (this.closing || this.grants.has(agent))
            throw new Error('AGENT_BINDING_UNAVAILABLE');
        const grant = this.ledger.authorize(subject, taskId, agent.id);
        this.grants.set(agent, grant);
        this.boundAgents.add(agent);
        owner.effect(() => () => { this.grants.delete(agent); this.boundAgents.delete(agent); });
        return grant;
    }
    /** Agent object identity matters; a reused session id does not restore a grant. */
    current(agent) {
        if (this.closing || !agent || this.ctx.agents.get(agent.id) !== agent)
            throw new Error('UNBOUND_AGENT');
        const grant = this.grants.get(agent);
        if (!grant)
            throw new Error('UNBOUND_AGENT');
        this.ledger.assertCurrent(grant);
        return grant;
    }
    async readTicket(grant, ticketId, signal) {
        signal.throwIfAborted();
        // Replace this boundary with a tenant-authorized backend connector in production.
        await Promise.resolve();
        signal.throwIfAborted();
        return this.ledger.readTicket(grant, ticketId);
    }
    observeFinal(agent, facts) {
        // Revocation forbids data access, but must not erase the operation's audit identity.
        const grant = this.grants.get(agent);
        if (grant)
            this.ledger.audit(grant, 'tool-final-observed', facts);
    }
}
