# 限制回合数为什么仍可能失控：成本、延迟与预算

> 从源码理解 Agent Harness · 第 11 篇 · 成本、延迟与预算

给 Agent 设置“最多执行三轮”，是否就能保证成本有限、几分钟内结束？如果第一轮不断重试，如果每轮都要摘要历史，如果子任务再调用模型，三轮这个数字便很难说明真正消耗了什么。

DeepSeek Harness 有输出额度、目标回合数、重试策略、压缩次数和并发配额。它们各自有用，但约束对象不同。本文从资源消耗的实际层级出发，解释**为什么多个局部上限不会自动组成任务级预算**。

## 一个任务可能产生多类调用

Turn 中有 Step，Step 中有 attempt，工具结果可能使 Loop 继续下一 Step；child Agent 有自己的请求，压缩摘要也通过独立 LLM stream 调用。单看主 Agent 的回合数，无法覆盖全部模型使用。[步骤中的请求尝试](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L398-L544) [独立摘要调用](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/compaction/compaction-basic/src/summarizer.ts#L120-L180) [子 Agent 的执行](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/subagent/subagent-in-process-driver/src/index.ts#L158-L207)

例如“修复缺陷并通过测试”启动一次自动回合，先读文件，再改代码，再分析失败测试；请求重试和上下文摘要可能发生在这些步骤之间。最终只增加一轮目标计数，模型请求却已经不止一次。

![成本、延迟与预算的机制图](assets/11-budgets.png)

这张图列的是现有局部控制及其范围，统一任务预算是应用需要另行设计的能力。把图上的几个配置名称汇总成一个界面面板，不会改变它们在代码里的作用域。

## maxTokens 限制的是本次输出

精确模型路由解析可以补默认 maxTokens，也校验 reasoning effort。请求参数的输出上限有助于控制单次生成，但输入历史、其他 attempt、摘要和 child 调用并不因此停止消耗。[模型默认额度与能力解析](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/llm/llm/src/index.ts#L885-L918)

max-tokens finish 也不是普通成功：Turn 会保留截断停止信息，摘要器则拒绝把截断摘要当作完整 checkpoint。主回答或摘要被截断，后续可能需要恢复，反而增加额外调用。[回合中的截断结果](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L296-L395) [摘要截断拒绝](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/compaction/compaction-basic/src/summarizer.ts#L196-L209)

因此输出额度需要与任务类型匹配。无限增大可能增加单次消耗，过小又可能导致反复修复。源码规定的是控制位置，适合某类任务的额度仍需根据实际输入与完成质量评测。

## 目标额度不限制同一 Step 的重试

maxGoalRounds 在目标准入和 user/message fold 中限制已接纳的自动回合。被拒绝的排队消息不计，已经进入某一回合的多个步骤与请求尝试也不各算新 round。[目标回合计数](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/goal/goal/src/fold.ts#L313-L331)

normal retry 检查 maxRetries，但 always 不使用这项次数上限；maxDelayMs 只控制一次退避时长。一个请求可以一直停留在同一 Step，等待和重试，目标计数保持不变。[重试次数与延迟策略](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/llm/llm-retry/src/index.ts#L188-L259)

这不是配置名称写错，而是额度对象不同。目标额度防止自动回合无限推进，重试策略处理请求恢复；如果任务要求总时长或总调用数有限，还需要覆盖这两层的共同截止条件。

工具 timeout 也只约束被包装的执行过程，协作式取消可能继续等待底层静止。超时配置不能直接等同于“任务必定在这个秒数内返回并释放全部资源”。[工具 deadline 与等待](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/guard/timeout-policy/src/index.ts#L55-L81)

## 输入测量与供应商用量不能混为账单

token meter 估算请求视图压力，用于决定是否压缩。供应商返回的 TokenUsage 则描述一次实际模型调用的计数，输入与缓存字段明确互斥。

```typescript
/**
 * Token accounting for one model call (cache fields are optional).
 *
 * Counts are DISJOINT: `inputTokens` is uncached input only; cached input is
 * reported separately as `cacheReadTokens`/`cacheWriteTokens` (billed input =
 * sum of the three). Adapters whose providers fold cache hits into a total
 * prompt count (DeepSeek's `prompt_tokens`) subtract them out.
 */
export interface TokenUsage {
  inputTokens: number
  outputTokens: number
  /**
   * Exact full-call total including aggregate prompt and output tokens.
   *
   * Adapters preserve a provider total or derive it from authoritative
   * aggregate prompt/output counters; they omit it when unavailable or
   * inconsistent.
   */
  totalTokens?: number
  cacheReadTokens?: number
  cacheWriteTokens?: number
  reasoningTokens?: number
}
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/llm/llm/src/types.ts#L167-L189)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

inputTokens 是未缓存输入，cacheReadTokens 和 cacheWriteTokens 分别计数，不能把供应商已包含缓存的总输入再次加一次。totalTokens 是可信总量存在时才提供，不是所有路由都能随意推导。reasoningTokens 也不应在未核对 adapter 语义和计费规则时额外叠加成另一份费用。

如果应用做内部成本核算，应记录 provider、model、调用目的、usage 和所使用的计费版本。实际价格需要相应时点的供应商资料；本文不使用假定价格生成金额，也不把 token 估算写成实际账单。

摘要有自己的 usage。仅聚合主 Loop 的正常 assistant 输出，会漏掉摘要或其他调用；只统计成功请求，也可能漏掉供应商对失败或部分输出的实际计量。系统需要明确数据缺失时是估计还是未知，而不是填零来获得漂亮总数。

## 预留输出空间也是预算设计

compaction-basic 在压力路径解析模型窗口，结合输出预留生成压缩策略，再检查测量值。

```typescript
}
const spec = resolveCompactSpec(
  policy,
  info.context.contextWindow,
  reservedCompletionTokens(agent, info.defaultMaxTokens),
)
if (measurement.totalTokens < spec.thresholdTokens) return null
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/compaction/compaction-basic/src/index.ts#L313-L319)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

输入空间和输出空间不能各自最大化后拼在一起。预留不足可能造成生成截断，过早压缩又可能频繁增加摘要成本。裁剪先落地、重测再决定是否摘要，可以减少某些不必要调用，但不代表对全部任务都达到最优成本。[压力阈值、裁剪与重测](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/compaction/compaction-basic/src/index.ts#L278-L346)

压缩的结果还影响未来请求：较小视图可能降低后续输入量，也可能因遗漏信息增加恢复工作。评估是否值得，应该比较完整任务的成本与质量，而不是只看一次摘要节省多少 token。

## 延迟来自多种有意等待

模型首字延迟只是其中一部分。有序工具 prepare、用户审批、前序慢结果、持久 flush、摘要请求和取消排空都会进入关键路径。提高工具并行度，只能改变可并行 body 的重叠程度，不能消除这些等待。[有序提交的等待](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/tool-calls.ts#L60-L290) [执行前存储屏障](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-checkpoint-policy/src/index.ts#L54-L83)

资源治理还有限定范围。maxParallelToolCalls 管一个 Loop，job 配额管对应 owner，child 深度与数量管委派；它们不直接约束累计 token 或跨 Agent 供应商额度。[工具并行度](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/constants.ts#L1-L6) [作业活跃计数](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/jobs/jobs-local/src/index.ts#L30-L61) [子 Agent 容量](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/subagent/subagent/src/index.ts#L189-L202)

测量延迟时，应分开记录接纳、准备、派发、首字、结算和清理完成。否则一个慢工具与一次用户等待会被误归为模型慢，优化方向也会偏离真实原因。

## 怎样增加真正的任务级预算

若产品需要硬额度，可以建立任务级资源账本，在请求、摘要和 child 准入时预留额度，结算时用可靠 usage 对账；达到条件后撤销自动推进并传播统一取消。还要定义用量未知、预留未结算和迟到结果的处理。这是新增设计建议，源码没有因此已经拥有统一金额控制器。

预留与实际结算必须分开。并发请求若都只检查“现在还有预算”，可能同时通过而超额；取消后费用也可能继续结算。与作业 stopping 计数一样，额度回收应跟随真实生命周期，不能只跟随用户点击。

低风险文本工具未必需要完整账本，配置有限 retry 和合理输出额度可能足够。需要财务或时间承诺的持续 Agent，则应建立覆盖所有调用目的和生命周期的策略。

## 技术心得：预算首先是作用域与计量口径

这次分析让我更明确，预算不是几个数字的集合，而是“谁在何时为哪些消耗负责”。回合数、attempt 数、估算 token、实际 usage 和金额都能有价值，但必须明确转换关系与缺失信息。

DSH 提供局部控制，优势是位置清楚、容易组合；不足是上层需要补跨调用预算与统一截止。研究没有真实价格测算、p95 延迟或容量压测；既有 retry、compaction 和生命周期测试只支持相关控制机制。下一篇会讨论怎样用事件与遥测观察这些真实执行阶段。

---

研究基线：DeepSeek Harness `0.2.1-alpha.1`，提交 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。源码事实以该版本为准；文中的工程判断和改造建议另行说明。教学场景不代表真实模型业务实测。

源码与运行记录可从[证据索引](../appendices/evidence-index.md)和[验证附录](../appendices/validation.md)复核。本文引用此前同一提交的验证结果，本轮写作不将其重新计为新测试。

[专栏目录](README.md) · [上一篇](10-autonomy.md) · [下一篇](12-observability.md)
