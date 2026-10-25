import type { Context } from '@deepseek-ai/cordis'
import Schema from '@deepseek-ai/schemastery'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'research-sum-tool'
export const inject = ['tools']
export interface Config { enabled: boolean }
export const Config: Schema<Config> = Schema.object({
  enabled: Schema.boolean().default(true),
})

/** Register a conditional, cancellable arithmetic capability in the owning scope. */
export function apply(ctx: Context, config: Config): void {
  ctx.tools.register(defineTool({
    name: 'research_sum',
    description: 'Return the sum of two finite numbers.',
    parameters: {
      a: { type: 'number', required: true },
      b: { type: 'number', required: true },
    },
    output: {
      schema: { type: 'number' },
      render: (_args, value) => [{ type: 'text', text: String(value) }],
    },
    isConcurrencySafe: () => true,
    async execute(args, exec) {
      exec.signal.throwIfAborted()
      const value = args.a + args.b
      if (!Number.isFinite(value)) throw new RangeError('sum must be finite')
      return value
    },
  }), { when: () => config.enabled })
}
