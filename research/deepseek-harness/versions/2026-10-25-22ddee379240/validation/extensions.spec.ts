import { describe, expect, it } from 'vitest'
import { SessionId } from '@deepseek-ai/dsh-session'
import { createUserMessage, ToolCallId } from '@deepseek-ai/dsh-llm'
import * as Sum from '../examples/sum-tool/lib/index.js'
import * as Route from '../examples/route-policy/lib/index.js'
import { runtime, ScriptAdapter, send, sumCall, text } from './mock-runtime.ts'

describe('current extension contracts', () => {
  it('commits a canonical sum and feeds it into the second real Loop request', async () => {
    const adapter = new ScriptAdapter([sumCall({ a: 2, b: 3 }), text('5')])
    const ctx = await runtime(adapter)
    try {
      const plugin = ctx.plugin(Sum, { enabled: true }); await plugin
      const handle = await ctx.agents.create({ sessionId: SessionId('sum'), agentOptions: { provider: 'mock', model: 'base' } })
      try {
        await send(handle.agent, '2 + 3')
        expect(adapter.requests).toHaveLength(2)
        expect(adapter.requests[1]?.messages.some(m => m.role === 'tool' && m.content.some(b => b.type === 'text' && b.text === '5'))).toBe(true)
        expect(handle.agent.session.snapshotEvents().at(-1)).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'completed' } } })
      } finally { await handle.dispose() }
      await plugin.dispose()
      expect(ctx.tools.get('research_sum')).toBeUndefined()
    } finally { await ctx.fiber.dispose() }
  })
  it('rejects invalid model JSON arguments as INVALID_ARGS', async () => {
    const adapter = new ScriptAdapter([sumCall({ a: 'bad', b: 3 }), text('invalid')])
    const ctx = await runtime(adapter)
    try {
      await ctx.plugin(Sum, { enabled: true })
      const h = await ctx.agents.create({ sessionId: SessionId('invalid'), agentOptions: { provider: 'mock', model: 'base' } })
      try {
        await send(h.agent, 'bad input')
        expect(JSON.stringify(h.agent.session.snapshotEvents().filter(e => e.type === 'tool/result'))).toContain('INVALID_ARGS')
      } finally { await h.dispose() }
    } finally { await ctx.fiber.dispose() }
  })
  it('omits a disabled tool from the request and refuses a forged call', async () => {
    const adapter = new ScriptAdapter([sumCall({ a: 2, b: 3 }), text('denied')])
    const ctx = await runtime(adapter)
    try {
      await ctx.plugin(Sum, { enabled: false })
      const h = await ctx.agents.create({ sessionId: SessionId('disabled'), agentOptions: { provider: 'mock', model: 'base' } })
      try {
        await send(h.agent, 'try a hidden tool')
        expect(adapter.requests[0]?.tools?.some(t => t.name === 'research_sum')).not.toBe(true)
        expect(JSON.stringify(h.agent.session.snapshotEvents().filter(e => e.type === 'tool/result'))).toContain('UNKNOWN_TOOL')
      } finally { await h.dispose() }
    } finally { await ctx.fiber.dispose() }
  })
  it('invalidates an admitted definition when its registration unloads', async () => {
    const ctx = await runtime(new ScriptAdapter([]))
    try {
      const plugin = ctx.plugin(Sum, { enabled: true }); await plugin
      const h = await ctx.agents.create({ sessionId: SessionId('withdraw'), agentOptions: { provider: 'mock', model: 'base' } })
      try {
        const signal = new AbortController().signal
        const toolSet = await ctx.tools.resolve({ agent: h.agent, modelSelection: { provider: 'mock', model: 'base' }, signal })
        try {
          await plugin.dispose()
          const batch = await ctx.tools.execute({ calls: [{ type: 'tool-call', id: ToolCallId('withdrawn'), name: 'research_sum', arguments: '{"a":2,"b":3}' }], agent: h.agent, signal, toolSet })
          expect(JSON.stringify(batch)).toContain('UNKNOWN_TOOL')
        } finally { toolSet.dispose() }
      } finally { await h.dispose() }
    } finally { await ctx.fiber.dispose() }
  })
  it('scopes creation routing and keeps the durable selection after plugin unload', async () => {
    const adapter = new ScriptAdapter([text('scoped'), text('plain'), text('retained')])
    const ctx = await runtime(adapter)
    try {
      let disposeRoute: (() => Promise<void>) | undefined
      const scoped = await ctx.agents.create({ sessionId: SessionId('scoped'), agentOptions: { provider: 'mock', model: 'base' }, setup: async agentCtx => {
        const plugin = agentCtx.plugin(Route, { provider: 'mock', model: 'policy' }); await plugin
        disposeRoute = async () => { await plugin.dispose() }
      } })
      const plain = await ctx.agents.create({ sessionId: SessionId('plain'), agentOptions: { provider: 'mock', model: 'base' } })
      try {
        await send(scoped.agent, 'scoped'); await send(plain.agent, 'plain')
        await disposeRoute?.()
        await send(scoped.agent, 'retained')
        expect(adapter.requests.map(r => r.model)).toEqual(['policy', 'base', 'policy'])
        expect(scoped.agent.session.snapshotEvents().some(e => e.type === 'model/selection')).toBe(true)
      } finally { await scoped.dispose(); await plain.dispose() }
    } finally { await ctx.fiber.dispose() }
  })
  it('captures a model at step preparation and applies a later selection on the next step', async () => {
    const adapter = new ScriptAdapter([sumCall({ a: 2, b: 3 }), text('done')])
    const ctx = await runtime(adapter)
    try {
      await ctx.plugin(Sum, { enabled: true })
      const h = await ctx.agents.create({ sessionId: SessionId('next-step'), agentOptions: { provider: 'mock', model: 'base' }, setup: agentCtx => {
        agentCtx.on('agent/pre-step', async ({ agent, step }, next) => {
          if (step === 1) agent.model.select({ provider: 'mock', model: 'policy' })
          return next()
        })
      } })
      try {
        await send(h.agent, 'change during preparation')
        expect(adapter.requests.map(r => r.model)).toEqual(['base', 'policy'])
      } finally { await h.dispose() }
    } finally { await ctx.fiber.dispose() }
  })
  it('refuses the historical agent/request routing override before a model call', async () => {
    const adapter = new ScriptAdapter([])
    const ctx = await runtime(adapter)
    try {
      ctx.on('agent/request', async (_event, next) => ({ ...await next(), model: 'legacy' }))
      const h = await ctx.agents.create({ sessionId: SessionId('legacy'), agentOptions: { provider: 'mock', model: 'base' } })
      try {
        await send(h.agent, 'legacy override')
        expect(adapter.requests).toHaveLength(0)
        expect(JSON.stringify(h.agent.session.snapshotEvents())).toContain('agent.model.select()')
      } finally { await h.dispose() }
    } finally { await ctx.fiber.dispose() }
  })
  it('cancels a streaming call and commits its visible prefix before idle', async () => {
    const adapter = new ScriptAdapter(['hang'])
    const ctx = await runtime(adapter)
    try {
      const h = await ctx.agents.create({ sessionId: SessionId('cancel'), agentOptions: { provider: 'mock', model: 'base' } })
      try {
        const partial = new Promise<void>(resolve => {
          const off = ctx.on('agent/assistant-stream', ({ frame }) => {
            if (frame.type === 'chunk' && frame.chunk.type === 'text-delta') { off(); resolve() }
          })
        })
        h.agent.followup(createUserMessage({ content: [{ type: 'text', text: 'cancel' }], source: { kind: 'user' } }))
        await partial
        h.agent.cancel({ kind: 'user' })
        await h.agent.whenIdle()
        const events = h.agent.session.snapshotEvents()
        expect(events.at(-1)).toMatchObject({ type: 'turn/end', data: { reason: { kind: 'aborted' } } })
        expect(events.some(e => e.type === 'assistant/message')).toBe(true)
      } finally { await h.dispose() }
    } finally { await ctx.fiber.dispose() }
  })
})
