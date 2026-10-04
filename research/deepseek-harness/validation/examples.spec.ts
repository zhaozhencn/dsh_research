import { describe, expect, it } from 'vitest'
import { SessionId } from '@deepseek-ai/dsh-session'
import * as Sum from '../examples/sum-tool/lib/index.mjs'
import * as Route from '../examples/route-policy/lib/index.mjs'
import { createUserMessage } from '@deepseek-ai/dsh-llm'
import { runtime, ScriptAdapter, send, sumCall, text } from './mock-runtime.ts'

describe('source-pinned extensions', () => {
  it('limits a route listener mounted in setup to its Agent scope', async () => {
    const adapter = new ScriptAdapter([text('scoped'), text('unscoped')])
    const ctx = await runtime(adapter)
    try {
      const scoped = await ctx.agents.create({sessionId: SessionId('research-scoped'), agentOptions: {provider:'mock',model:'base'}, setup: async agentCtx => {await agentCtx.plugin(Route,{provider:'mock',model:'policy'})}})
      const plain = await ctx.agents.create({sessionId: SessionId('research-plain'),agentOptions:{provider:'mock',model:'base'}})
      await send(scoped.agent,'scoped'); await send(plain.agent,'plain')
      expect(adapter.requests.map(r=>r.model)).toEqual(['policy','base'])
      await scoped.dispose(); await plain.dispose()
    } finally {await ctx.fiber.dispose()}
  })
  it('executes registered tool and feeds its canonical result into the next real Loop step', async () => {
    const adapter = new ScriptAdapter([sumCall({ a: 2, b: 3 }), text('5')])
    const ctx = await runtime(adapter)
    try {
      const mounted = ctx.plugin(Sum); await mounted
      const handle = await ctx.agents.create({ sessionId: SessionId('research-sum'), agentOptions: { provider: 'mock', model: 'base' } })
      await send(handle.agent, '2 + 3')
      const events = handle.agent.session.snapshotEvents()
      expect(adapter.requests).toHaveLength(2)
      expect(adapter.requests[1]?.messages.some(m => m.role === 'tool' && m.content.some(b => b.type === 'text' && b.text === '5'))).toBe(true)
      expect(events.filter(e => e.type === 'step/start')).toHaveLength(2)
      expect(events.at(-1)).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'completed' } } })
      await handle.dispose()
      await mounted.dispose()
      expect(ctx.tools.get('research_sum')).toBeUndefined()
    } finally { await ctx.fiber.dispose() }
  })
  it('returns a structured invalid-argument failure without running a malformed tool', async () => {
    const adapter = new ScriptAdapter([sumCall({ a: 'bad', b: 3 }), text('invalid')])
    const ctx = await runtime(adapter)
    try {
      await ctx.plugin(Sum)
      const handle = await ctx.agents.create({ sessionId: SessionId('research-invalid'), agentOptions: { provider: 'mock', model: 'base' } })
      await send(handle.agent, 'malformed')
      const event = handle.agent.session.snapshotEvents().find(e => e.type === 'tool/result')
      expect(event).toBeDefined()
      expect(JSON.stringify(event)).toContain('INVALID_ARGS')
      await handle.dispose()
    } finally { await ctx.fiber.dispose() }
  })
  it('routes through agent/request, retains logged state after unload, and stops affecting new agents', async () => {
    const adapter = new ScriptAdapter([text('before'), text('during'), text('retained'), text('fresh')])
    const ctx = await runtime(adapter)
    try {
      const handle = await ctx.agents.create({ sessionId: SessionId('research-route'), agentOptions: { provider: 'mock', model: 'base' } })
      await send(handle.agent, 'before')
      const mounted = ctx.plugin(Route, { provider: 'mock', model: 'policy' }); await mounted
      await send(handle.agent, 'during')
      expect(adapter.requests.map(r => r.model)).toEqual(['base', 'policy'])
      expect(handle.agent.session.snapshotEvents().filter(e => e.type === 'request/header').at(-1)).toMatchObject({ data: { header: { config: { model: 'policy' } } } })
      await mounted.dispose()
      // Unload removes the listener, not the durable request header.
      await send(handle.agent, 'retained')
      expect(adapter.requests.at(-1)?.model).toBe('policy')
      const fresh = await ctx.agents.create({ sessionId: SessionId('research-fresh'), agentOptions: { provider: 'mock', model: 'base' } })
      await send(fresh.agent, 'fresh')
      expect(adapter.requests.at(-1)?.model).toBe('base')
      await fresh.dispose()
      await handle.dispose()
    } finally { await ctx.fiber.dispose() }
  })
  it('cancels a streaming turn and settles its visible prefix before idle', async () => {
    const adapter = new ScriptAdapter(['hang'])
    const ctx = await runtime(adapter)
    try {
      await ctx.plugin(Route, { provider: 'mock', model: 'policy' })
      const handle = await ctx.agents.create({ sessionId: SessionId('research-cancel'), agentOptions: { provider: 'mock', model: 'base' } })
      const partial = new Promise<void>(resolve => {
        const off = ctx.on('agent/assistant-stream', ({ frame }) => {
          if (frame.type === 'chunk' && frame.chunk.type === 'text-delta') { off(); resolve() }
        })
      })
      handle.agent.followup(createUserMessage({ content: [{ type: 'text', text: 'cancel me' }], source: { kind: 'user' } }))
      await partial
      handle.agent.cancel({ kind: 'user' })
      await handle.agent.whenIdle()
      const events = handle.agent.session.snapshotEvents()
      expect(events.at(-1)).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'aborted' } } })
      expect(events.some(e => e.type === 'assistant/message')).toBe(true)
      expect(adapter.requests).toHaveLength(1)
      await handle.dispose()
    } finally { await ctx.fiber.dispose() }
  })
})
