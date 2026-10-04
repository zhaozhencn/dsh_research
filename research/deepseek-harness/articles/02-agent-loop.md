# 一次输入如何推进为多步执行：拆解 Agent Loop

> 从源码理解 Agent Harness · 第 02 篇 · Agent Loop 与执行模型

用户输入“修改这个函数，再运行测试”，界面只出现一次发送操作。运行时却可能调用模型几次：先判断要读哪些文件，再执行工具，再根据结果修改，最后整理答案。此时把 Agent 简化成“模型调用加一个 while 循环”，已经不足以解释消息接纳、失败恢复和结束时机。

DeepSeek Harness 的 Agent Loop 将一次执行分成 Turn、Step 和 attempt。本文围绕一次代码修复输入，追踪这三层怎样协作，以及为什么**循环的正确性往往取决于提交顺序，而不只取决于继续条件**。

## 一个回合里，有多个步骤和请求尝试

Turn 是回合，Step 是回合中的一步，attempt 是该步骤的一次模型请求尝试。一个带工具调用的 Step 通常不会直接结束 Turn：工具结果先写回历史，下一 Step 再交给模型。若请求失败后允许重试，同一 Step 又可能包含多个 attempt。

这种分层让系统可以分别回答：用户输入何时被接纳、工具结果在哪一步产生、重试是否重复消费消息，以及哪个回合被取消。若把它们都记成一次 run，错误排查会失去必要的粒度。

Loop 也不是创建 Agent 的全部过程。Registry 先准备 Session 和 Agent scope，执行 setup，再发布实例。创建选项中的 agentOptions 是嵌套结构，不能与内部 Loop 创建方法的参数混用。setup 把能力准备好，运行才随后通过输入启动。[Registry 创建入口](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent/src/index.ts#L358-L415) [实例准备、发布与清理](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/index.ts#L479-L640) [创建参数定义](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent/src/index.ts#L64-L118)

### 第一步：创建入口与执行状态机先分开

从调用者常用的 `ctx.agents.create()` 往下看，Registry 不直接把一次模型请求当作 Agent：

```typescript
async create(options: CreateAgentOptions): Promise<AgentHandle> {
  const ownerCtx = this.ctx
  // Re-trace a Service-backed factory through the accessing context
  // explicitly. This preserves AgentLoop's dependency origin while binding
  // its effects to ownerCtx; plain factories receive ownerCtx as an explicit
  // capability and need no Cordis tracker magic.
  const { target } = this.requireFactory()
  const receiver = getTraceable(ownerCtx, target)
  // oxlint-disable-next-line typescript/unbound-method -- Reflect.apply intentionally supplies the caller-traced receiver
  return Reflect.apply(target.createAgent, receiver, [ownerCtx, options])
}
```

[源码：`packages/core/agent/src/index.ts:391–401`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent/src/index.ts#L391-L401)。

`ownerCtx` 捕获此次访问的注册上下文；requireFactory 要求已有执行工厂，getTraceable 把服务工厂的资源归属追踪到调用方，Reflect.apply 再进入 createAgent。这个额外的接线层让 Registry 可以保持 Agent 生命周期接口，而实际执行模型由工厂提供。创建一个会话对象、注册一个 Agent 和启动一次回合，是三个相关但不同的动作。

Loop Agent 的构造还会恢复回合边界，并建立自己的输入、上下文和提示视图：

```typescript
this.requestSurfaceGeneration = session.surface.contentGeneration
this.dispatch = agentEvents(loopCtx, this)
this.scope = createScope(loopCtx, this)
this.ctx = this.scope.ctx
this.inbox = new ReactLoopInbox(this.ctx.sessionProjections, session, this.dispatch)
/* v8 ignore next -- the loop registers its own turnBoundary unit, so the key is always present */
const lastTurn = this.loopCtx.sessionProjections.stateOf(session, 'turnBoundary')?.lastTurn ?? 0
this.phase = { kind: 'idle', lastTurn }
this.runtimeContext = new RuntimeContextProjection(this.ctx, session)
this.systemPrompt = new SystemPromptProjection(session)
```

[源码：`packages/core/agent-loop/src/agent.ts:128–137`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L128-L137)。

`contentGeneration` 保存初始 surface 代际，dispatch 绑定真实 Agent，scope 承载实例贡献；inbox 使用会话投影，不是另造一份随意可改的数组。`lastTurn` 从 turnBoundary 投影取得，phase 初始 idle。因此恢复之后编号可以延续，而机器不会在构造函数里自动重放已经执行的工具。

阅读后续代码时，应始终带着三个索引：Turn 对应一次输入处理的边界，Step 对应一次模型决策及工具反馈，attempt 对应一次供应商请求。比如 Step 2 的第一次请求超时、第二次请求成功，日志应显示一个 Step 内两次尝试，而不是两个用户任务。用这些身份关联审计和延迟，才能区分“模型慢”与“重试多”。

![图2：一次请求如何成为历史](assets/02-agent-loop-02.png)

图2：同一 Step 可以产生多个 attempt。详见本节及相邻源码解读；图示省略其他分支。

## 输入 API 实际上选择了接纳时机

`followup` 进入 next-turn 队列并唤醒 Agent；`steer` 进入 next-step 队列并唤醒；`inject` 同样进入 next-step，却不单独唤醒 idle Agent。`send` 根据当前运行与取消状态选择队列，是便捷入口，不能固定解释为“排下一轮”。[输入、取消与 idle 等待](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L154-L241)

例如模型正在请求读文件，用户补充“暂时不要修改”。steer 可以让这条指令在后续 Step 边界被考虑；它不回溯撤销已经启动的读取。followup 更适合一个独立的后续要求。如果当前 Agent idle，只 inject 一条上下文，并不会开始执行任务。

队列变更记录成 `agent/inbox/spliced`。preStep claim 取出下一步的候选输入，其中第一步可以消费一条 next-turn，随后主要消费 next-step。每个 Agent 只有一个 driver 预留槽位，输入追加不会为同一实例启动第二条并行控制链。这里限制的是单 Agent 推进，不是多个 Agent 的全局并发。[Inbox 的 claim 实现](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/inbox.ts#L109-L148)

![Agent Loop 与执行模型的机制图](assets/02-agent-loop.png)

图1：从输入到多步骤循环。

### 第二步：消息落在哪个队列，要在同步插入之前决定

```typescript
send(message: UserMessage, target: InboxTarget, wakeup: boolean): void {
  // Waking input cannot join an aborted activity, so it starts the next turn.
  // Captured before the insertion so a reentrant cancel from a splice observer cannot reclassify it.
  const wakingAfterAbort = wakeup && this.phase.kind !== 'idle' && this.phase.abort.signal.aborted
  const resolvedTarget = wakingAfterAbort ? 'next-turn' : target
  this.inbox.splice(resolvedTarget, Infinity, 0, [message])
  if (wakeup) this.wakeDriver(wakingAfterAbort)
}

followup(input: UserMessage): void {
  this.send(input, 'next-turn', true)
}

steer(input: UserMessage): void {
  this.send(input, 'next-step', true)
}

inject(input: UserMessage): void {
  this.send(input, 'next-step', false)
}
```

[源码：`packages/core/agent-loop/src/agent.ts:154–173`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L154-L173)。

第一处判断把“唤醒输入到达已取消的活动”分类为 next-turn。它在 inbox.splice 之前完成：入队会同步通知观察者，观察者可能立刻 cancel；如果插入之后才读取 abort 状态，同一输入会被通知副作用重新分类。resolvedTarget 由插入前的事实决定，才有稳定语义。

followup、steer、inject 的差别就是 target 和 wakeup 两个参数。inject 能改变下一步材料，却不会独自启动 idle 机器；steer 请求尽快在下一 Step 接纳，但不会修改当前已经冻结的模型请求。要实现“立即停止写文件”，必须另外触发取消或执行策略，而不是只补一句 steer 文本。

### 第三步：claim 一批候选，不代表这批输入已经进入模型历史

```typescript
claim(target: InboxTarget, turn: number): UserMessage[] {
  const claimed = this.mutate('next-step', 0, this.nextStep.length, [], false)
  if (target === 'next-turn') claimed.push(...this.mutate('next-turn', 0, 1, [], false))
  for (const message of claimed) this.dispatch.emit('agent/inbox/claimed', { message, turn })
  return claimed
}
```

[源码：`packages/core/agent-loop/src/inbox.ts:109–114`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/inbox.ts#L109-L114)。

先取走全部 next-step；在 next-turn 边界才额外取一条 next-turn。最后逐条发布 claimed 通知。这种组合避免把后续独立请求全部塞进当前回合，也允许多条补充上下文一起参与一次准入。claim 是队列消费，`user/message` 才是会话接纳事实；拒绝后的恢复责任因此需要相关插件明确承担。

唤醒的另一半在 wakeDriver：

```typescript
private wakeDriver(wakeAfterAbort = false): void {
  if (this.phase.kind !== 'idle') {
    // Maintenance and aborted drivers cannot deliver the wake: latch it for
    // replay at convergence. Live drivers claim queued work themselves;
    // disposal never latches, so teardown waits on no model turn.
    const reason = abortedCancelCause(this.phase.abort.signal)
    if (reason?.kind !== 'disposed' && (this.phase.kind === 'maintenance' || wakeAfterAbort)) {
      this.phase.wakeRequested = true
    }
    return
  }
  const driver = Promise.withResolvers<void>()
  this.activityDone = driver.promise
  this.setPhase({
    kind: 'running',
    abort: new AbortController(),
    turn: this.phase.lastTurn,
    step: 0,
    wakeRequested: false,
  })
  this.loopCtx.agents.withInitiator(this, () => this.kick()).then(driver.resolve, driver.reject)
}
```

[源码：`packages/core/agent-loop/src/agent.ts:214–235`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L214-L235)。

已有活动时不创建第二条 driver，只在 maintenance 或取消后的等待阶段留下 wakeRequested；disposed 不留下唤醒。idle 时先把 phase 改成 running，再进入带 initiator 的 kick，避免同步观察者把它误认为仍可再开一个 driver。这是单实例串行槽位，不是全系统只能运行一个 Agent。

一个边界例子是取消期间又收到“继续处理下一件事”：新消息排 next-turn，当前活动先结算，wake latch 在收束后重新检查队列；如果队列已经被清空，就不为丢失的输入额外启动模型。

## preStep：候选输入成为请求之前

真正的执行不是入队后立刻向供应商发送请求。Loop 先打开 Turn，进入 preStep，claim 输入，组装提示词和 runtime context，再把候选交给 `agent/pre-step` waterfall。

```typescript
const claimed = this.inbox.claim(target, position.turn)
const assembly = await this.loopCtx.systemPrompt.assemble(assembleContextFor(this, signal))
signal.throwIfAborted()
const sections = renderContextSections(assembly)
const context = this.runtimeContext.project(joinContextSections(sections), sections)
const decision = await this.dispatch.waterfall(
  'agent/pre-step', { messages: claimed, ...position, signal },
  (): Promise<PreStepDecision> => Promise.resolve<PreStepDecision>({
    kind: 'enter',
    messages: context === undefined ? claimed : [...claimed, context],
  }),
)
signal.throwIfAborted()
if (decision.kind === 'reject') return decision
return { ...decision, assembly }
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L271-L285)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

这段代码有两处时序值得注意。第一，assembly 先于准入 waterfall；插件可能在准入过程中决定拒绝，已经组装过上下文并不代表用户消息已进入模型历史。第二，每次 await 之后检查 signal，让异步组装期间发生的取消能够生效。

若准入 reject，Turn 可以以 blocked 结束而没有 Step；初始消息为空时也可能正常关闭而不调用模型。接纳之后，Loop 才打开 `step/start` 并开始准备请求。因此观察一个 turn/start，不能推导它一定产生过模型请求。[Turn 的准入与闭合分支](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L296-L395)

### 第四步：准入控制的是 Step 提案，而不是已发送请求

原文 preStep 片段先 assembly 再 waterfall。这里有两种失败路径：组装阶段 signal 检查失败，候选还没有形成请求；准入钩子返回 reject，回合已有开始事实，但仍然没有 Step。

```typescript
while (true) {
  signal.throwIfAborted()
  const step = phase.step + 1
  const decision = await this.preStep(target, { turn, step })
  if (decision.kind === 'reject') {
    turnEnds = { kind: 'blocked' }
    return false
  }
  if (turnEnds && decision.messages.length === 0) break
  // A removed waking message or an enter decision rewritten to empty
  // still owns the initial turn boundary, but it spends no model call.
  if (phase.step === 0 && decision.messages.length === 0) {
    turnEnds = { kind: 'completed' }
    return false
  }
  signal.throwIfAborted()
  this.session.append('step/start', { turn, step })
  phase.step = step
```

[源码：`packages/core/agent-loop/src/agent.ts:313–330`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L313-L330)。

`decision.kind === 'reject'` 给 Turn blocked 结果并退出；空的首批消息给 completed 并退出。只有剩余路径才追加 step/start，然后推进 phase.step。这使“Turn 打开”“Step 打开”“模型调用开始”各有证据，不能用一个 loading 状态概括。

特别留意 `turnEnds && decision.messages.length === 0`：在已有停止候选时，新的边界没有补充材料就结束；如果 stopping 钩子此前补了输入，下一 preStep 仍能形成一个新 Step。Loop 并没有把第一次 completed 当成不可撤销的最终结束。

准入插件应把完整 identified message 批次和 startsRequestSeries 一起向上传递。只返回 enter 却遗漏其他插件的消息，会改变本次接纳内容；在 async next 前读到有效权限，返回后也要检查它仍有效。第一篇的目标准入正是这种包围式检查的实例。

![图3：执行单位与状态归属](assets/02-agent-loop-03.png)

图3：阶段状态和产品成功需要独立解释。详见本节及相邻源码解读；图示省略其他分支。

## 从路由准备到工具结果回流

请求阶段先运行 `agent/request`，允许插件确定 provider、model 等配置，再通过 prepareCall 绑定适配器与能力。随后根据路由更新能力调整 prompt projection，首次 attempt 记录接纳的 user 消息，buildRequest 派生并冻结消息与请求配置。[请求准备和构建](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L547-L686) [PreparedCall 的绑定](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/llm/llm/src/index.ts#L929-L1018)

模型开始输出时，live 通道可以立即发送字块。正常结算后，Loop 先追加 `assistant/message`，再发布 committed end frame。模型输出一开始就可见，与最终结果已经进入 Session，是两个不同状态；字块也不是每个都单独持久存储。[实时输出的结算](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/assistant-stream.ts#L45-L110)

若模型请求工具，Loop 将调用转换为调度任务，记录 `tool/call`，执行准备、授权、body 和结果处理，再按模型顺序追加 `tool/result`。例如读取函数的结果成为后续请求中的 tool 消息，模型才有条件根据真实内容决定修改。

当前 Step 结束时写 `step/end`。工具结果通常要求下一 Step 继续；该请求重新从当时的 Session surface 派生，携带先前结果。现有研究的 V05 扩展测试确实断言了第二次 adapter 请求包含工具结果 5，而不是只检查工具曾被注册。[工具调度与结果提交](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/tool-calls.ts#L60-L290)

### 第五步：先准备真实路由，再提交此次输入

```typescript
const proposedConfig = await this.dispatch.waterfall(
  'agent/request', { turn, step, signal },
  () => Promise.resolve(seedConfig),
)
signal.throwIfAborted()
if (!proposedConfig.provider || !proposedConfig.model) {
  throw new Error(`agent "${this.id}" has no provider/model: set AgentOptions.provider and AgentOptions.model or supply both via the agent/request waterfall`)
}
```

[源码：`packages/core/agent-loop/src/agent.ts:576–583`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L576-L583)。

agent/request waterfall 从 seedConfig 出发，插件可决定路由；等待后先检查取消，再检查 provider/model 是否齐全。该阶段看到的是提交前历史，不能认为本次候选 user 消息早已对所有请求插件可见。随后 prepareCall 绑定 adapter 和精确能力，成功后才协调提示投影。

```typescript
const { config, preparedCall } = await this.prepareRequest(turn, step, signal)
const startsRequestSeries = firstAttempt && decision.startsRequestSeries === true
const commits = this.systemPrompt.project(renderedPrompt, {
  inHistory: preparedCall?.systemPromptUpdate === 'in-history',
  startsSeries: startsRequestSeries
    || this.requestSurfaceGeneration !== this.session.surface.contentGeneration
    || (preparedCall?.toolUpdate === undefined && this.toolsChanged(assembly.tools)),
})
for (const { message, intent } of commits) {
  this.session.append('system/message', { turn, step, message }, intent)
}
if (firstAttempt) {
  for (const message of decision.messages) {
    this.session.append('user/message', message, { surfaceOp: 'append' })
  }
}
firstAttempt = false
const request = this.buildRequest(config, preparedCall, assembly.tools, { turn, step }, startsRequestSeries, signal)
```

[源码：`packages/core/agent-loop/src/agent.ts:408–425`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L408-L425)。

这段把输入只提交一次的规则写得非常明确。每次 attempt 都重新 prepareRequest；systemPrompt.project 根据绑定能力决定保留或改写提示历史；user/message 只在 firstAttempt 为 true 时追加。firstAttempt 随即转为 false，而 while 还可以继续。于是重试可以使用新的 surface，却不会把用户问题复制到历史里。

buildRequest 冻结 route、tools 和 deriveMessages 的结果。下一次动态配置刷新影响后面的 attempt，不应让已经开始的一次发送同时混用旧能力与新实现。完整绑定协议放在第 03 篇。

### 第六步：可见字块与结算消息各有提交点

```typescript
const stream = preparedCall?.stream(request) ?? this.loopCtx.llm.stream(request)
signal.throwIfAborted()
live.start()
started = true
for await (const chunk of stream) {
  signal.throwIfAborted()
  live.push(chunk)
}
signal.throwIfAborted()
```

[源码：`packages/core/agent-loop/src/agent.ts:436–444`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L436-L444)。

取得异步流后先检查 signal，再发 live start；每次迭代在 push 之前检查 signal，流结束后再检查。push 提供用户实时可见内容，但最后的完整消息还没有追加。网络已返回一些文字，不代表可以生成“结果已保存”的产品通知。

```typescript
live.settle(
  'assistant/message',
  () => this.session.append('assistant/message', {
    turn,
    step,
    message,
    ...live.usage === undefined ? {} : { usage: live.usage },
    stream: live.stream,
  }, { surfaceOp: 'append' }).seq,
)
if (finish.kind === 'max-tokens') return { kind: 'max-tokens' }
```

[源码：`packages/core/agent-loop/src/agent.ts:520–530`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L520-L530)。

live.settle 包住同步 append，assistant/message 保存本 Step 的消息、usage 和 compact stream；append 成功才发布 committed end。finish 为 max-tokens 则返回对应停止原因，不能把一个被截断的回答视为普通完成。实时 stream 和 durable settlement 共享内容来源，减少显示和历史各自组装造成的差异。

### 第七步：工具反馈决定下一次模型看见什么

```typescript
let next = 0
let concluded = false
while (next < planned.length) {
  // Commit before classifying again so registry changes affect unstarted calls.
  // oxlint-disable-next-line typescript/no-non-null-assertion -- bounded by the loop condition
  const first = planned[next]!
  const mode = ctx.tools.executionMode(first.exec).kind
  const group = mode === 'parallel' ? planned.slice(next) : [first]
  const outcome = await runGroup(
    ctx, turn, step, group, mode, signal, acceptContext,
  )
  next += outcome.consumed
  concluded ||= outcome.concluded
  if (outcome.aborted) {
    for (const call of planned.slice(next)) appendSkippedToolCall(session, turn, step, call.block)
    return { concluded }
  }
}
return { concluded }
```

[源码：`packages/core/agent-loop/src/tool-calls.ts:83–101`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/tool-calls.ts#L83-L101)。

next 是本批工具的推进位置；每组执行之前重新查看注册表的 executionMode，独占工具构成单项屏障，允许并行的组进入有限池。outcome.consumed 推进位置，concluded 累积结束意图；若组已 aborted，剩余工具追加 skipped 事实，避免后续恢复把它们误认为未记录执行状态。

body 完成与 tool/result 提交不是同一时刻。runGroup 按模型顺序结算，新增上下文进入 next-step；Loop 完成当前 Step 后，下一 Step 从最新 surface 派生消息。一个有效集成测试应检查第二次 adapter 请求里的 tool 消息，而不只检查工具 execute 曾被调用。

以“读函数—修改—解释结果”为例，模型第一次给工具调用，工具返回实际内容；随后模型才有依据形成修改。工具结果若没进入历史，即使文件读取真的发生过，决策链仍然断开。

## 结束信号之后，为什么还要检查一次

模型没有工具调用，或工具声明 concludesTurn，可能使当前步骤具备结束条件。Loop 仍不能马上写 turn/end，因为 next-step 输入和 turn-stopping 扩展可能提出后续工作。

```typescript
    this.session.append('step/end', { turn, step })
  }
  signal.throwIfAborted()
  if (turnEnds && this.inbox.nextStep.length === 0) {
    await this.dispatch.serial('agent/turn-stopping', { turn, signal })
    signal.throwIfAborted()
  }
  if (turnEnds && this.inbox.nextStep.length === 0) break
  target = 'next-step'
}
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L356-L365)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

先确认没有 next-step，再等待串行 `agent/turn-stopping`，等待之后重新检查 signal 和队列。工作区变更记录等插件可以在这里完成收尾，期间新输入也可能改变循环能否结束。两次队列检查并非重复代码，而是覆盖一个异步等待窗口。

`max-tokens` 还有特殊处理：一旦成为 Turn 的停止结果，后续正常步骤不会把它降为 completed。失败发生在已经打开的 Step 内时，finally 关闭 Step，必要时先补齐工具结果；尚未打开 Step 的失败则不走同样的闭合路径。[回合停止与错误收尾](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L296-L395) [步骤与 attempt 循环](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L398-L544)

### 第八步：停止候选要经过队列与扩展的最后收束

原文 stopping 片段的两个 nextStep 检查夹住一个 await。第一次检查判断是否适合调用收尾插件；第二次检查确认插件等待期间没有新的继续材料。这是异步控制流的不变量，不能删成一次检查以减少重复。

停止原因还有一项单调规则：

```typescript
// max-tokens is sticky: once any step hits the ceiling, later steps
// that complete normally must not downgrade the turn outcome.
const stepEnd = await this.step(decision)
// max-tokens stays sticky: a later completed step must not
// downgrade the turn outcome.
if (turnEnds === null || turnEnds.kind !== 'max-tokens') turnEnds = stepEnd
```

[源码：`packages/core/agent-loop/src/agent.ts:336–341`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L336-L341)。

只要任意 Step 触及 max-tokens，后续 Step 正常结束不能把 Turn 改回 completed。否则产品会丢掉回合中曾经发生截断这一事实。stepEnd 为 null 时只是继续候选，最终 Turn 原因还需要看后续工作。

```typescript
} finally {
  try {
    // oxlint-disable-next-line typescript/no-non-null-assertion -- every exit assigns a turn ending
    this.session.append('turn/end', { turn, reason: turnEnds! })
  } catch (error: unknown) {
    this.throwError(error)
  }
}
if (!this.inbox.hasPending) return false
phase.abort = new AbortController()
// A fresh controller makes a latch set on the old one stale: the live driver claims the queue itself.
phase.wakeRequested = false
phase.step = 0
return true
```

[源码：`packages/core/agent-loop/src/agent.ts:382–395`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L382-L395)。

finally 尝试追加 turn/end；追加失败必须报告，不能对外声称已完整结算。完成后如果 inbox 还有 pending，换新的 AbortController、清除旧 wake latch、把 step 重置为零，才允许下一 Turn 开始。新的回合不能继承前一个回合已经 aborted 的 signal。

这段也提示应用：当 UI 看见“Step 结束”，还有 stopping、Turn 结算与可能的下一 Turn；whenIdle 才是机器静止的等待入口，但仍不是存储或业务验收屏障。

![图4：结束判定为何不能提前](assets/02-agent-loop-04.png)

图4：await 之后仍可能出现输入或生命周期变化。详见本节及相邻源码解读；图示省略其他分支。

## 重试、取消和 idle 的真实含义

请求重试位于 Step 内。preStep assembly 通常不重做，inbox 不再次消费，接纳的 user 消息不重复记录；每个 attempt 则重新准备路由与请求。恢复插件如果改变了 surface，下一请求会使用改变后的历史。这既避免重复输入，也允许上下文修复。

取消会向当前 Turn 传播 AbortSignal。已经启动的模型或工具需要合作终止，Loop 等待它们结算之后才真正回到 idle。可见文本可能保存为 interrupted assistant 消息，未启动工具与未知结果工具则按实际记录修补。

因此 `whenIdle` 只表示 driver 已经静止。请求可能失败，任务可能被取消，磁盘也可能还需要 flush。接口调用者应检查 turn/end 的原因，按需要显式等待存储屏障。用“await whenIdle 然后宣布业务成功”的方式接入，会同时混淆执行、验收和持久化三种状态。

### 第九步：重试保留 Step，另记一次失败 attempt

```typescript
const action = await this.dispatch.waterfall(
  'agent/request-error', {
    turn,
    step,
    provider: request.provider,
    failure: finish.failure,
    retryPolicy: preparedCall?.retryPolicy,
    signal,
  },
  () => Promise.resolve<RequestErrorAction>(undefined),
)
signal.throwIfAborted()
if (action?.kind !== 'retry') {
  throw new LlmError(finish.failure.message, finish.failure.code, finish.failure)
}
continue
```

[源码：`packages/core/agent-loop/src/agent.ts:494–509`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L494-L509)。

失败 finish 已先结算 assistant/attempt，再进入 request-error waterfall。failure 与实际 provider、retryPolicy 一并提供，等待后检查取消。只有 action.kind 为 retry 才 continue；否则抛 LlmError。这里的 continue 返回同一 step 的内部 while，不会返回 preStep，也不会重放工具 body。

因此“重试一次”必须注明对象。请求重试与新的目标回合不同，异常修复器更不能把每种错误都转换为 retry，否则插件程序错误也会被无意义供应商请求掩盖。

### 第十步：cancel 关闭继续权，whenIdle 等待真实收束

```typescript
cancel(cause: AgentCancelCause, options: CancelOptions = {}): void {
  if (!options.keepInbox) {
    this.inbox.clear()
    if (this.phase.kind !== 'idle') this.phase.wakeRequested = false
  }
  if (this.phase.kind !== 'idle') this.phase.abort.abort(cause)
}
```

[源码：`packages/core/agent-loop/src/agent.ts:175–181`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L175-L181)。

默认取消先清 inbox，再 abort 活动；keepInbox 政策允许保留后续输入。abort 是请求停止，没有把 activityDone 直接 resolve，也没有立即宣布 idle。模型 iterator、工具 dispatch 和资源 owner 仍要结算。

```typescript
async whenIdle(): Promise<void> {
  let activity: Promise<void>
  do {
    await (activity = this.activityDone)
  } while (activity !== this.activityDone)
}
```

[源码：`packages/core/agent-loop/src/agent.ts:237–242`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L237-L242)。

等待捕获的 activityDone 之后，再比较它是否被新活动替换。如果收束过程中 latched wake 启动了新活动，就继续等新的 promise。这比只保存一次 promise 更准确，但同样不承担“将来永远没有新消息”的保证。

还有一个容易遗漏的状态：maintenance 对外 status 也表现为 idle，但内部 phase 不是 idle，wakeDriver 会延后唤醒。不能凭 status 字符串自行假设 runMaintenance 可以重入。调用 API 的内部 phase 检查和等待协议比状态展示更严格。[maintenance 的外部状态](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L140-L141)

```typescript
runMaintenance<T>(job: (signal: AbortSignal) => Promise<T>): Promise<T> {
  if (this.phase.kind !== 'idle') throw new Error(`agent "${this.id}" already has active work`)
  const done = Promise.withResolvers<void>()
  const maintenance: Phase = {
    kind: 'maintenance',
    abort: new AbortController(),
    lastTurn: this.phase.lastTurn,
    wakeRequested: false,
  }
  this.setPhase(maintenance)
  this.activityDone = done.promise
```

[源码：`packages/core/agent-loop/src/agent.ts:183–193`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L183-L193)。

maintenance 建立自己的 signal 与 activityDone，释放之前保持生命周期。它可用于不启动模型回合的维护工作；应用应依据 Handle、signal 和 whenIdle 管理资源，而不是绕过运行时直接改变 phase。

### 一次正常与一次异常怎样落在日志里

|事件阶段|正常读取后回答|第二步请求失败后重试|
|---|---|---|
|输入接纳|Turn 1／Step 1 首次追加 user/message|同样只追加一次|
|工具反馈|Step 1 记录 assistant/message 与 tool/result|工具事实保留，不因请求失败重做|
|下一步|Step 2 发出新请求并回答|Step 2 attempt 1 记录 assistant/attempt|
|恢复|无需 retry|request-error 返回 retry，仍在 Step 2|
|完成|step/end、turn/end completed|attempt 2 成功后再正常结算|

表格是由源码推导的教学时序，不是新增实测记录。遇到取消则应检查 interrupted 消息、aborted Turn 与在途工作结算，而不能把没有最终文本当成唯一取消证据。

## 分层控制带来的收益与复杂度

收益是执行历史有明确粒度：每一轮输入、每一步工具反馈、每次失败请求都有位置。Loop 可以保持统一的执行机制，而重试、压缩、上下文和审批由扩展参与。工具结果回流也成为显式事实，便于测试和恢复。

复杂度集中在跨层顺序。插件必须知道自己运行在 pre-step、request、request-error 还是 stopping；入队不等于接纳，live 输出不等于提交，结束信号不等于已结束。若扩展在错误阶段写入事实，历史可能与实际行为不一致。

这也是我从 Loop 源码得到的技术心得：**循环应围绕可检查的不变量组织，而不是围绕“模型说继续还是停止”组织。** 输入只提交一次，工具结果按规定顺序进入历史，取消后不增加新派发，等待之后重新确认生命周期，都是比一个布尔继续条件更有价值的设计要求。

这套思路适合多步骤 Agent 和事件驱动工作流。对一次性纯文本请求，不一定需要照搬全部分层；但只要开始加入工具、并发输入和恢复，就需要明确相同类型的时序约束。Loop、cancel、request-error 与示例中的受控模型测试验证了选定路径；真实供应商流式取消、吞吐和整套界面没有由这些测试证明。

### 第十一步：生命周期关闭必须等待执行和存储各自的屏障

```typescript
  if (machine !== undefined) {
    machine.cancel({ kind: 'disposed' })
    await machine.whenIdle()
    await machine.scope.dispose()
  }
} catch (error: unknown) {
  failures.push(error)
}
// The loop above committed its closing events synchronously into the
// session; handle close drains them durably before releasing the write
// path. The close drain can be the first operation that surfaces a
// durability failure, so its error is retained, not logged away.
try {
  await handle?.close()
} catch (error: unknown) {
  failures.push(error)
```

[源码：`packages/core/agent-loop/src/index.ts:543–558`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/index.ts#L543-L558)。

owner 先 cancel disposed，等待 machine.whenIdle，再关闭实例 scope；之后尝试持久 handle.close，把 Loop 最后同步追加的事件排空到写路径。执行停止、能力注销、存储排空有各自责任，失败被收集并在清理后报告，而不是发生首个错误就放弃剩余释放。

这种分层的优势在于故障能按提交点解释：输入未接纳、供应商失败、工具结果未结算、Turn 结束记录失败和持久关闭失败不会都压成一个 unknown run。代价是调用者必须选对等待对象；如果自己只等工具 body 的 Promise，就跳过了历史提交和其他在途工作。

技术上我最关注的三个不变量是：firstAttempt 阻止输入重复提交；new AbortController 阻止下一 Turn 继承取消；whenIdle 的 promise 重查阻止等待漏掉收束后的新活动。这些小片段比一幅“LLM—Tools—LLM”图更能说明成熟执行器的设计。

原研究的 loop、cancel、request-error 和真实扩展测试支持相应受控路径；本文增加的是源码解释。业务成功应继续沿第一篇的独立验收定义判断，真实供应商取消响应与生产并发吞吐需要另行验证。

---

研究基线：DeepSeek Harness `0.2.1-alpha.1`，提交 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。源码事实以该版本为准；文中的工程判断和改造建议另行说明。教学场景不代表真实模型业务实测。

源码与运行记录可从[证据索引](../appendices/evidence-index.md)和[验证附录](../appendices/validation.md)复核。本文引用此前同一提交的验证结果，本轮写作不将其重新计为新测试。

[专栏目录](README.md) · [上一篇](01-task-completion.md) · [下一篇](03-model-adaptation.md)
