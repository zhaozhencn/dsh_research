# 如何控制自动推进：规划模式、目标续跑与人工接管

> 从源码理解 Agent Harness · 第 10 篇 · 自主性控制与人工干预

用户批准计划之后，Agent 应该立刻执行所有动作吗？自动目标运行中，用户点击暂停，已经排队的下一轮能否继续？模型连续重复同一个工具，发一条提醒是否就保证它停止？这些问题都涉及自主性，却不能靠一个 auto 开关回答。

DeepSeek Harness 将自动续跑、规划状态、敏感操作审批、输入接纳与取消分别实现。本文关注它们怎样决定推进权限，尤其是**已经准备的动作如何在授权变化后失效**。

## 自主性要沿执行阶段控制

目标 driver 决定 idle 后是否主动发下一轮；规划模式决定接下来遵循的工作政策；审批决定某个敏感工具能否执行；steer、followup 和 cancel 则为外部干预提供不同接纳位置。[自动目标续跑](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/goal/goal-round-driver/src/index.ts#L137-L205) [退出规划的用户审阅](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/plan/plan-mode/src/index.ts#L277-L348) [工具审批](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/interaction/user-approval/src/index.ts#L215-L307) [输入与取消](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L154-L241)

例如代码修复先处于规划模式，用户审阅计划；批准后进入实施，修改受保护资源还可能再次 ask；目标尚未完成时可以自动续跑，用户也可以暂停。这些控制各有状态与时机，不是一次批准取得全程无限行动权。

设计产品时，应该给用户说明“当前允许继续什么”，而不是只显示自动或手动。自动推进的权限、计划批准和资源写入授权分开，才容易解释拒绝和接管。

![自主性控制与人工干预的机制图](assets/10-autonomy.png)

## 计划批准为什么不立即写最终状态

exit_plan_mode 先读取并检查计划文件，准备用户审阅请求，等待 answerer。它要求符合约束的批准结果，不接受随意一条自由回复作为肯定。下面片段体现了精确选择条件。

```typescript
const reviewItems = answer.answers.filter(entry => entry.id === REVIEW_ID)
const item = reviewItems.length === 1 ? reviewItems[0] : undefined
if (item?.selected.length !== 1 || item.selected[0] !== APPROVE_LABEL || item.custom !== undefined) {
  const feedback = item?.custom ?? ''
  throw new Error(feedback === ''
    ? 'The user chose to keep planning; revise the plan and present it again.'
    : `The user chose to keep planning; their feedback: ${feedback}`)
}
// Keep plan guidance for the rest of this assistant tool batch. The
// silent selection is appended at the next accepted in-turn pre-step,
// before its request assembly.
this.pendingIntents.set(agent.session, { active: false, narrate: false })
return { approved: true }
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/plan/plan-mode/src/index.ts#L340-L352)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

只有一项对应审阅答案，恰好选择批准，且没有 custom 回复，才保存 `active: false` 的 pending intent。拒绝或反馈会保持规划，并将原因交回模型，等待期间发生卸载或取消也不能冒充批准。[计划读取与等待期间检查](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/plan/plan-mode/src/index.ts#L277-L348)

pending intent 意味着“选择已经形成，尚待合适执行边界提交”。它让当前工具 batch 保留原规划政策，避免批准工具后，同一批后续操作无声地跨入新模式。

## 准入成功之后，再提交模式事实

plan-mode 监听 pre-step，先 await next，让下游准入决策完成，然后检查拒绝、signal 和 pending，再调用 onBoundary。

```typescript
ctx.on('agent/pre-step', async (
  { agent, signal },
  next,
): Promise<PreStepDecision> => {
  const decision = await next()
  const pending = this.pendingIntents.get(agent.session)
  if (decision.kind === 'reject' || signal.aborted || pending === undefined) return decision
  const narration = this.narration(agent.session, pending.active)
  try {
    this.onBoundary(agent.session)
  } catch (error) {
    ctx.logger.warn('dsh-plan-mode: failed to append selected plan mode at step start: %o', error)
    return decision
  }
  return !pending.narrate || narration === undefined
    ? decision
    : { ...decision, messages: [...decision.messages, narration] }
})
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/plan/plan-mode/src/index.ts#L196-L213)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

若下游 reject 或取消，不提交模式改变；提交失败记录告警，pending 不应被当作已落地事实。叙述消息也只在实际需要时添加。这种顺序让政策选择和事件记录保持对应，而不是在用户点击后立即宣布所有执行边界都已切换。[模式事件的边界提交](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/plan/plan-mode/src/index.ts#L418-L453)

还有一项需要结合调用方才能看清的细节：Loop preStep 在进入 waterfall 前先组装提示词。规划段的 text 回调可以读取 pending intent，因此本次 assembly 已按待应用选择构造；后续 accepted waterfall 才提交 plan/mode。源码局部注释里的“request assembly 前”不能取代这条完整调用链的时序。[Loop 组装与 waterfall 顺序](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L267-L285) [规划段的 pending 读取](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/plan/plan-mode/src/index.ts#L196-L224)

这里并非矛盾，而是区分临时选择和已确认事实。提示词可以根据待应用意图准备，日志则必须等待接纳条件成立。

## Host 暂停怎样阻止旧续跑

目标 driver 为下一轮保留 goalId、revision、round 和 messageId，追踪 queued、claimed、admitted。目标改变或普通用户输入到达时，旧 reservation 可能变 stale。准入 waterfall 前后重查，checkpoint await 后也重查 live Agent 与状态。[驱动器的有效性检查](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/goal/goal-round-driver/src/index.ts#L96-L134) [准入双重校验](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/goal/goal-round-driver/src/index.ts#L350-L459)

Host 外部发起 pause 时，driver 根据 currentInitiator 与当前执行状态决定取消正在运行的 Turn，并保留需要保留的其他 inbox。模型在自己 Turn 中改变状态与外部 Host 接管位于不同边界，不能省略来源判断后写成同一种行为。[目标暂停、竞争输入与错误观察](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/goal/goal-round-driver/src/index.ts#L246-L344)

假设第 2 轮在 checkpoint 等待中，用户暂停后又立即恢复。revision 的变化使旧 attempt 不能误暂停新目标，也不能重新取得新目标的准入权。系统必须验证同一个生命周期、同一份授权，而不只是“现在存在一个同名目标”。

自动 activation 与持久 phase 也分开。错误、max-tokens、卸载和恢复可能撤销进程内自动权限，目标仍然可以展示为未完成。这样的保守设计避免把失败恢复直接转成新一轮外部动作。[目标激活与持久状态](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/goal/goal/src/index.ts#L240-L280)

## 人工输入在哪里接管，决定了影响范围

steer 在后续 Step 边界被接纳，followup 排下一 Turn，inject 不单独唤醒 idle Agent，cancel 则请求停止当前在途工作。取消默认清空队列，keepInbox 可保留；但保留消息并不使失效目标 revision 自动重新合法。

例如用户只想补充“修改前先展示 diff”，steer 比取消再重建任务更贴近意图；若要立刻停止敏感操作，应使用取消与 provider 的停止能力。已经完成的副作用无法凭输入接纳撤回，接管效果仍受执行阶段限制。

产品按钮需要映射到这些真实语义。界面写“暂停”，实现却只是 followup 一条自然语言消息，当前工具可能继续运行；这会使用户预期与运行事实错位。按钮含义应由控制 API 与资源停止过程决定。

## 提醒属于软干预，不能替代终止策略

repeat-tool-reminder 观察重复调用，向后续上下文补充提醒，不阻止 body 派发。它可能帮助模型调整，但不提供强制停止不变量。[重复工具提醒的实际行为](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/guard/repeat-tool-reminder/src/index.ts#L188-L239)

硬约束需要明确额度、deny、取消、deadline 或应用验收策略。计划提示同样只是工作政策的一部分：运行时的工具授权和 sandbox 才限制真实资源访问，不能把“规划模式”直接称为不可突破的只读沙箱。

这并不贬低软引导。成本低、可解释、允许模型恢复思路的提醒适合低风险探索；敏感操作则应由可执行规则兜底。两种方式可以组合，但要清楚它们提供不同强度的保证。

## 优势、不足与技术心得

DSH 将自主性控制分布到真实执行边界，模式意图延迟提交，续跑授权使用 revision 和生命周期校验，人工接管有明确 API。这些机制适合持续任务与插件组合。

不足是上层产品需要把多种状态组织成清楚的用户体验；规划、目标、审批和取消若各自只展示一段文案，用户很难理解当前到底拥有什么权限。模型仍可能不遵循软提醒，provider 也可能不能立即停止，框架并未消除这些限制。

我的技术心得是：自主性应被设计为可撤销的执行权。授权取得、等待期间的复核、具体动作准入和权限撤销，都需要记录；只在任务开始时检查一次，无法覆盖长任务中的状态变化。

V08 目标权限与 driver 测试、V10 规划 66 项验证受控来源、批准和接纳边界。完整人机界面与真实模型长期服从性未运行。后续预算篇会继续讨论：即使推进权限正确，如何使资源消耗可预测。

---

研究基线：DeepSeek Harness `0.2.1-alpha.1`，提交 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。源码事实以该版本为准；文中的工程判断和改造建议另行说明。教学场景不代表真实模型业务实测。

源码与运行记录可从[证据索引](../appendices/evidence-index.md)和[验证附录](../appendices/validation.md)复核。本文引用此前同一提交的验证结果，本轮写作不将其重新计为新测试。

[专栏目录](README.md) · [上一篇](09-security.md) · [下一篇](11-budgets.md)
