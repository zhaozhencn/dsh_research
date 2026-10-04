import { SessionId } from '@deepseek-ai/dsh-session';
import * as Policy from './policy.js';
import * as TicketTool from './ticket-tool.js';
/** Invoke from trusted application code AFTER SSO, ownership and task authorization. */
export async function createEnterpriseAgent(ctx, subject, taskId, sessionId) {
    const approved = ctx.enterprisePlatform.ledger.authorize(subject, taskId, sessionId);
    return ctx.agents.create({
        sessionId: SessionId(sessionId),
        agentOptions: { provider: approved.provider, model: approved.model, maxTokens: approved.maxTokens },
        setup: async (agentCtx, agent) => {
            const grant = ctx.enterprisePlatform.bind(agentCtx, agent, subject, taskId);
            const timer = setTimeout(() => agent.cancel({ kind: 'hook', reason: 'enterprise-task-deadline' }), Math.min(Math.max(1, grant.expiresAt - Date.now()), 2_147_483_647));
            timer.unref();
            agentCtx.effect(() => () => { clearTimeout(timer); });
            await agentCtx.plugin(Policy);
            await agentCtx.plugin(TicketTool);
            return { commit: () => ctx.enterprisePlatform.ledger.assertCurrent(grant) };
        },
    });
}
