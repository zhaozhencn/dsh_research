import type { Context } from '@deepseek-ai/cordis'
import Schema from '@deepseek-ai/schemastery'
import type {} from '@deepseek-ai/dsh-agent'

export const name = 'research-route-policy'
export const inject = ['agents']
export interface Config { provider: string; model: string }
export const Config: Schema<Config> = Schema.object({
  provider: Schema.string().required(),
  model: Schema.string().required(),
})

/** Select a durable route on creation; later explicit model choices remain authoritative. */
export function apply(ctx: Context, config: Config): void {
  if (!config.provider.trim() || !config.model.trim()) {
    throw new TypeError('provider and model must be nonempty')
  }
  ctx.on('agent/created', ({ agent }) => {
    agent.model.select({ provider: config.provider, model: config.model })
  })
}
