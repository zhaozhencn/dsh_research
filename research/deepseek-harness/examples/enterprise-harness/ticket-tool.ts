import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'
import type {} from './platform.js'
import { TICKET_TOOL } from './policy.js'

export const name = 'enterprise-ticket-tool'
export const inject = ['tools', 'enterprisePlatform']

export function apply(ctx: Context): void {
  ctx.tools.register(defineTool({
    name: TICKET_TOOL,
    description: 'Read the ticket authorized for this enterprise task; return its id and version.',
    parameters: { ticketId: { type: 'string', required: true } },
    output: {
      schema: {
        type: 'object', additionalProperties: false,
        properties: {
          ticketId: { type: 'string', required: true }, title: { type: 'string', required: true },
          status: { type: 'string', required: true }, version: { type: 'integer', required: true },
        },
      },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
    },
    isConcurrencySafe: () => true,
    async execute(args, exec) {
      exec.signal.throwIfAborted()
      if (!/^[A-Z0-9-]{1,64}$/.test(args.ticketId)) throw new Error('INVALID_TICKET_ID')
      const grant = ctx.enterprisePlatform.current(exec.agent)
      const ticket = await ctx.enterprisePlatform.readTicket(grant, args.ticketId, exec.signal)
      exec.signal.throwIfAborted()
      // A revoke/dispose while awaiting the backend must prevent releasing data.
      ctx.enterprisePlatform.current(exec.agent)
      return ticket
    },
  }))
}
