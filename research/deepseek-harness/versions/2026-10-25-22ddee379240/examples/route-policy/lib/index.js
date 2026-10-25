import Schema from '@deepseek-ai/schemastery';
export const name = 'research-route-policy';
export const inject = ['agents'];
export const Config = Schema.object({
    provider: Schema.string().required(),
    model: Schema.string().required(),
});
/** Select a durable route on creation; later explicit model choices remain authoritative. */
export function apply(ctx, config) {
    if (!config.provider.trim() || !config.model.trim()) {
        throw new TypeError('provider and model must be nonempty');
    }
    ctx.on('agent/created', ({ agent }) => {
        agent.model.select({ provider: config.provider, model: config.model });
    });
}
