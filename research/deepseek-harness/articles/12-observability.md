# 如何还原 Agent 的行动：事实日志与反馈授权遥测

> 从源码理解 Agent Harness · 第 12 篇 · 可观测性与审计

用户看到“文件已经生成”，随后却找不到报告。控制台没有异常，远端遥测面板也没有对应记录。此时该相信模型回复、工具结果、交付声明，还是 collector？如果系统没有区分这些信息的产生与交接过程，可观测性反而会制造更多误解。

DeepSeek Harness 将 Session 事实日志、assistant 实时流、Session telemetry 和 product analytics 分开。本文沿一次问题排查解释这些链路，重点分析反馈授权遥测，以及**为什么后端交接成功不等于远端已持久接收**。

## 四种记录回答四类问题

Session ledger 记录回合、请求、工具、审批与领域事件，用来重建状态和还原操作。assistant live stream 提供低延迟字块与当前 attempt；Session telemetry 将选定记录外发；产品分析则关注自己的启用条件、身份和产品事件。[会话事实追加](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/session/src/index.ts#L718-L775) [实时输出结算](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/assistant-stream.ts#L45-L110) [遥测能力的组合](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/telemetry/otel/src/index.ts#L14-L34) [产品分析上报](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/client/product-analytics/src/index.ts#L76-L100)

一个 collector 不可用，不应推导本地事实停止记录；关闭遥测，也不意味着用户看不到实时输出。反过来，界面显示了一段文本，不代表文本已经进入持久日志，或发送到外部。

把这些职责分开有助于定位问题。先确认本地操作事实，再检查是否有外发授权和捕获，再检查队列及传输。若一开始就只搜索远端日志，可能把“未被授权上传”误判成“工具没有执行”。

![可观测性与审计的机制图](assets/12-observability.png)

## 默认 Session OTel 为什么不是实时全量追踪

base 配置采用反馈授权捕获。OTel reporter 组合通用 coordinator 时明确指定 on-demand 和 includeHistory，而不是持续订阅每个普通事件并自动上报。用户提交新的反馈，才为相应会话前缀提供捕获依据。[默认遥测配置](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/bundle/base/cordis.patch.yml#L188-L216) [反馈授权与捕获](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry-otel/src/index.ts#L218-L250)

通用 coordinator 本身支持 live 与 on-demand 两种捕获方式；是否持续观察由消费方选择。把它拥有 live 能力，误写成默认产品持续上传，是忽略配置与 consumer 后容易产生的结论错误。

反馈判定位于 OTel reporter，检查事件是否属于 Session 自有后缀，并检查涉及 Session 身份的反馈类型。

```typescript
function isFeedback(session: Session, event: SessionEvent): boolean {
  if (event.seq < session.inheritedEventCount) return false
  switch (event.type) {
    case 'feedback/record': return true
    case 'feedback/message-put':
    case 'feedback/message-delete': return event.data.sessionId === session.id
    default: return false
  }
}
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry-otel/src/index.ts#L45-L53)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

fork 继承的旧反馈不能自动成为新 Session 的授权。reporter 还要求通知中的事件确实是 canonical log 中同一对象；直接 emit 一个同名事件，不会替代真正的反馈提交。离线反馈路径也从已提交快照重建并限制捕获边界，不把恢复产生的生命周期标记一并冒充该次提交。[canonical 反馈身份检查](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry-otel/src/index.ts#L218-L250)

## 捕获的是授权前缀，不是单独反馈文本

coordinator.captureSession 从已有交接游标后读取日志，限定 throughSeq，逐事件复制和处理。第一次授权可能包含之前的请求、工具与历史上下文，后续对同一活 Session 的捕获再从游标继续。[授权前缀与逐事件捕获](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry/src/coordinator.ts#L151-L164)

这意味着用户提交反馈时，隐私范围不仅是那几句反馈文字。应用应根据实际捕获策略决定需要脱敏哪些字段，怎样向用户解释记录范围，以及 collector 如何保留和删除数据。本文没有验证线上保存政策。

游标是以 Session 对象为键的模块级 WeakMap，跟随同一对象的进程内生命周期，有助于 reporter 重挂后避免重复交接；它不是跨重启的 durable ACK 记录。新的对象、新的进程或 detached 恢复不能自然继承这份状态，因此不能承诺全局 exactly-once 外发。[进程内交接游标](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry/src/coordinator.ts#L45-L58)

## 复制、脱敏和交接的真实顺序

captureEvent 对 envelope 与 data 做副本，构造 ledger record，经过 `session-telemetry/record` waterfall，再交给 backend。后端可能稍后序列化，副本避免外部处理直接引用会话对象。脱敏发生在捕获时，on-demand 模式不能把它理解为事件追加时已经清洗。[事件复制与 redaction](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry/src/coordinator.ts#L180-L217)

```typescript
  return this.ctx.waterfall('session-telemetry/record', record, () => record)
}

/** Hand one redacted record to the backend, then advance its ledger cursor. */
private deliver(session: Session, pending: PendingRecord): void {
  this.backend.emit(pending.record)
  if (pending.seq !== undefined) handoffCursor.set(session, pending.seq)
}
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry/src/coordinator.ts#L206-L213)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

默认 next 返回原 record，表示没有附加脱敏规则。存在 seam 不等于部署已经脱敏。规则抛错时，局部 containment 会使该记录被扣留，其他事件可以继续；这同时意味着整段前缀不保证全部抵达。

deliver 先 backend.emit，再更新游标。这个游标只能说明“交给后端”，不能说明 collector 接收、存储、建立索引或满足审计保留。后端本身还有队列额度、请求字节限制和停机期限，最终是 best-effort 外发。[导出容量与停机边界](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry-otel/README.md#L30-L80) [ledger、ops 与交接语义](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/docs/subsystems/session-telemetry.md#L24-L60)

## 怎样用事件还原一次缺失交付物

回到报告找不到的例子。先检查批准是否形成 approval/decided，再检查模式变更是否形成 plan/mode，再看工具调用和最终结果，最后单独确认 deliverables/presented。

这些不是固定按名称排列的时序。present 在 tools/result 观察阶段追加声明，可能先于 Loop 记录 tool/result；应按 seq 和 callId 还原过程，而不能先画一条想象顺序再找证据。观察者失败也不改变既定工具 outcome，所以工具成功不能单独证明声明存在。[交付声明提交](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/tool-present/src/index.ts#L70-L108) [工具观察者的错误包含](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/tools/src/index.ts#L1694-L1713)

本地事实若完整，再检查是否出现授权反馈、捕获上限、脱敏扣留、后端失败或请求丢弃。没有授权记录时，远端没有这一前缀可能正是预期行为，而不是遥测故障。

DSH_TELEMETRY_DISABLED 会提前返回，不构建相应 reporter；产品分析又有独立开关和身份条件。运维界面应显示这些实际模式，避免用户期待每一步都存在远端 trace。[禁用模式的提前退出](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/session/session-telemetry-otel/src/index.ts#L151-L162)

## 审计要求更强时，需要增加什么

本地 ledger、受控捕获和 best-effort 上传适合问题反馈与调试。若业务要求长期强审计，则还要明确持久接收确认、重放去重、保留策略、访问权限、删除义务和用量数据的完整性。这些不能从已有 OTel 类名推出。

可能的改造方向是，将关键审计流写入专用持久通道，保存接收水位并定义重试和去重，再与可选产品遥测分开。它会增加运维与数据治理责任，不能把“全部上传”无条件当作成熟度提升。

## 技术心得：观测信息也有来源和提交语义

这套设计的优势是本地执行不依赖远端 collector，反馈授权明确，记录副本与异常包含减少观察链对运行的干扰。它的不足也来自选择：默认不是完整实时 trace，默认 seam 不替代脱敏，后端交接不替代强持久审计。

我的技术心得是，观测数据同样需要解释“来自哪里、何时确认、当前走到哪一层”。日志方法返回、record 入队和远端持久保存，不能用一个 uploaded 状态混合表示。这一原则在消息队列和审计系统中同样适用。

V08 的 coordinator 34、OTel 42、egress 4 项验证受控后端与授权路径；未连接线上 collector，也未验证其数据治理。下一篇会进一步讨论：测试怎样证明这些局部语义，而不夸大为整体业务正确。

---

研究基线：DeepSeek Harness `0.2.1-alpha.1`，提交 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。源码事实以该版本为准；文中的工程判断和改造建议另行说明。教学场景不代表真实模型业务实测。

源码与运行记录可从[证据索引](../appendices/evidence-index.md)和[验证附录](../appendices/validation.md)复核。本文引用此前同一提交的验证结果，本轮写作不将其重新计为新测试。

[专栏目录](README.md) · [上一篇](11-budgets.md) · [下一篇](13-evaluation.md)
