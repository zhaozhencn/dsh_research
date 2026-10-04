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

/** Routing only; model-visible text continues through logged Loop channels. */
export function apply(ctx: Context, config: Config): void {
  if (!config.provider.trim() || !config.model.trim()) {
    throw new TypeError('provider and model must be nonempty')
  }
  ctx.on('agent/request', async (event, next) => {
    event.signal.throwIfAborted()
    const downstream = await next()
    event.signal.throwIfAborted()
    return { ...downstream, provider: config.provider, model: config.model }
  })
}
