# 一次输入如何推进为多步执行：拆解 Agent Loop

> 从源码理解 Agent Harness · 第 02 篇 · Agent Loop 与执行模型

用户输入“修改这个函数，再运行测试”，界面只出现一次发送操作。运行时却可能调用模型几次：先判断要读哪些文件，再执行工具，再根据结果修改，最后整理答案。此时把 Agent 简化成“模型调用加一个 while 循环”，已经不足以解释消息接纳、失败恢复和结束时机。

DeepSeek Harness 的 Agent Loop 将一次执行分成 Turn、Step 和 attempt。本文围绕一次代码修复输入，追踪这三层怎样协作，以及为什么**循环的正确性往往取决于提交顺序，而不只取决于继续条件**。

## 一个回合里，有多个步骤和请求尝试

Turn 是回合，Step 是回合中的一步，attempt 是该步骤的一次模型请求尝试。一个带工具调用的 Step 通常不会直接结束 Turn：工具结果先写回历史，下一 Step 再交给模型。若请求失败后允许重试，同一 Step 又可能包含多个 attempt。

这种分层让系统可以分别回答：用户输入何时被接纳、工具结果在哪一步产生、重试是否重复消费消息，以及哪个回合被取消。若把它们都记成一次 run，错误排查会失去必要的粒度。

Loop 也不是创建 Agent 的全部过程。Registry 先准备 Session 和 Agent scope，执行 setup，再发布实例。创建选项中的 agentOptions 是嵌套结构，不能与内部 Loop 创建方法的参数混用。setup 把能力准备好，运行才随后通过输入启动。[Registry 创建入口](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent/src/index.ts#L358-L415) [实例准备、发布与清理](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/index.ts#L479-L640) [创建参数定义](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent/src/index.ts#L64-L118)

## 输入 API 实际上选择了接纳时机

`followup` 进入 next-turn 队列并唤醒 Agent；`steer` 进入 next-step 队列并唤醒；`inject` 同样进入 next-step，却不单独唤醒 idle Agent。`send` 根据当前运行与取消状态选择队列，是便捷入口，不能固定解释为“排下一轮”。[输入、取消与 idle 等待](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L154-L241)

例如模型正在请求读文件，用户补充“暂时不要修改”。steer 可以让这条指令在后续 Step 边界被考虑；它不回溯撤销已经启动的读取。followup 更适合一个独立的后续要求。如果当前 Agent idle，只 inject 一条上下文，并不会开始执行任务。

队列变更记录成 `agent/inbox/spliced`。preStep claim 取出下一步的候选输入，其中第一步可以消费一条 next-turn，随后主要消费 next-step。每个 Agent 只有一个 driver 预留槽位，输入追加不会为同一实例启动第二条并行控制链。这里限制的是单 Agent 推进，不是多个 Agent 的全局并发。[Inbox 的 claim 实现](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/inbox.ts#L109-L148)

![Agent Loop 与执行模型的机制图](assets/02-agent-loop.png)

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

## 从路由准备到工具结果回流

请求阶段先运行 `agent/request`，允许插件确定 provider、model 等配置，再通过 prepareCall 绑定适配器与能力。随后根据路由更新能力调整 prompt projection，首次 attempt 记录接纳的 user 消息，buildRequest 派生并冻结消息与请求配置。[请求准备和构建](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L547-L686) [PreparedCall 的绑定](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/llm/llm/src/index.ts#L929-L1018)

模型开始输出时，live 通道可以立即发送字块。正常结算后，Loop 先追加 `assistant/message`，再发布 committed end frame。模型输出一开始就可见，与最终结果已经进入 Session，是两个不同状态；字块也不是每个都单独持久存储。[实时输出的结算](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/assistant-stream.ts#L45-L110)

若模型请求工具，Loop 将调用转换为调度任务，记录 `tool/call`，执行准备、授权、body 和结果处理，再按模型顺序追加 `tool/result`。例如读取函数的结果成为后续请求中的 tool 消息，模型才有条件根据真实内容决定修改。

当前 Step 结束时写 `step/end`。工具结果通常要求下一 Step 继续；该请求重新从当时的 Session surface 派生，携带先前结果。现有研究的 V05 扩展测试确实断言了第二次 adapter 请求包含工具结果 5，而不是只检查工具曾被注册。[工具调度与结果提交](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/tool-calls.ts#L60-L290)

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

## 重试、取消和 idle 的真实含义

请求重试位于 Step 内。preStep assembly 通常不重做，inbox 不再次消费，接纳的 user 消息不重复记录；每个 attempt 则重新准备路由与请求。恢复插件如果改变了 surface，下一请求会使用改变后的历史。这既避免重复输入，也允许上下文修复。

取消会向当前 Turn 传播 AbortSignal。已经启动的模型或工具需要合作终止，Loop 等待它们结算之后才真正回到 idle。可见文本可能保存为 interrupted assistant 消息，未启动工具与未知结果工具则按实际记录修补。

因此 `whenIdle` 只表示 driver 已经静止。请求可能失败，任务可能被取消，磁盘也可能还需要 flush。接口调用者应检查 turn/end 的原因，按需要显式等待存储屏障。用“await whenIdle 然后宣布业务成功”的方式接入，会同时混淆执行、验收和持久化三种状态。

## 分层控制带来的收益与复杂度

收益是执行历史有明确粒度：每一轮输入、每一步工具反馈、每次失败请求都有位置。Loop 可以保持统一的执行机制，而重试、压缩、上下文和审批由扩展参与。工具结果回流也成为显式事实，便于测试和恢复。

复杂度集中在跨层顺序。插件必须知道自己运行在 pre-step、request、request-error 还是 stopping；入队不等于接纳，live 输出不等于提交，结束信号不等于已结束。若扩展在错误阶段写入事实，历史可能与实际行为不一致。

这也是我从 Loop 源码得到的技术心得：**循环应围绕可检查的不变量组织，而不是围绕“模型说继续还是停止”组织。** 输入只提交一次，工具结果按规定顺序进入历史，取消后不增加新派发，等待之后重新确认生命周期，都是比一个布尔继续条件更有价值的设计要求。

这套思路适合多步骤 Agent 和事件驱动工作流。对一次性纯文本请求，不一定需要照搬全部分层；但只要开始加入工具、并发输入和恢复，就需要明确相同类型的时序约束。Loop、cancel、request-error 与示例中的受控模型测试验证了选定路径；真实供应商流式取消、吞吐和整套界面没有由这些测试证明。

---

研究基线：DeepSeek Harness `0.2.1-alpha.1`，提交 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。源码事实以该版本为准；文中的工程判断和改造建议另行说明。教学场景不代表真实模型业务实测。

源码与运行记录可从[证据索引](../appendices/evidence-index.md)和[验证附录](../appendices/validation.md)复核。本文引用此前同一提交的验证结果，本轮写作不将其重新计为新测试。

[专栏目录](README.md) · [上一篇](01-task-completion.md) · [下一篇](03-model-adaptation.md)
