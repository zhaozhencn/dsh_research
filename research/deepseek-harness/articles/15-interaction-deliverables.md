# 如何把执行结果交给用户：协议、重连与交付物

> 从源码理解 Agent Harness · 第 15 篇 · 交互协议与交付物

用户发送任务后收到一个 messageId，页面接着显示模型字块，稍后出现“修改了两个文件”和一份报告。网络断开再连接，哪些信息可以补回？进程重启后，旧 diff 还能打开吗？这既是协议问题，也是产物保存问题。

DeepSeek Harness 把命令接纳、事实订阅、实时输出、文件声明和工作区记录分成不同能力。本文围绕一次代码修复交付，说明**用户看到的完成状态应来自对应事实，而不能只从一条 RPC 响应推导**。

## messageId 证明接纳，不证明任务完成

SDK prompt 先确认初始化，取得或创建 Session，在附件处理前后检查 live Agent，再 followup 并返回 messageId。

```typescript
if (!this.initialized) throw new Error('SDK server is not initialized')
const rec = await this.getOrCreateSession(params.sessionId)
// An agent-loop-only reload disposes the loop's agents while this record
// survives; a retained agent accepts followup() silently, so validate the
// record against the live registry before delivery.
this.assertLiveAgent(rec, params.sessionId)
const content = await durablePromptContent(this.ctx, params.contentBlocks)
// Attachment admission crosses an async boundary where shutdown or an
// agent-loop reload may detach the retained handle.
this.assertLiveAgent(rec, params.sessionId)
const message = createUserMessage({
  content,
  source: { kind: 'user' },
})
rec.handle.agent.followup(message)
return { messageId: message.id }
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/sdk/server/src/server.ts#L179-L194)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

两次 assertLiveAgent 覆盖异步附件准入窗口：旧 record 可能仍在 SDK 中，但 Agent-loop reload 已经卸载原 Agent。只有对象还在内存，不意味着它仍是 registry 中可执行实例。[SDK 消息准入](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/sdk/server/src/server.ts#L178-L194)

响应提供消息身份，不把后续所有活动独占分配给这条 prompt。同一 Session 可以追加输入，Turn 与 Step 的接纳边界决定实际消费位置。客户端应观察 inbox、user/message 与 Turn 事实，不能把“返回了 ID”显示成“模型已经执行”。

这也影响失败重试。若命令已经被接纳，客户端因为响应丢失再发送，可能产生第二条输入。carrier 重连恢复与业务命令重发应该分别设计，不能只用统一网络重试覆盖。

![交互协议与交付物的机制图](assets/15-interaction-deliverables.png)

## snapshot、journal 和 live stream 各有什么职责

RemoteSnapshotStream 每个连接 generation 先取得完整 baseline，再应用 delta；重试期间保留旧视图，直到新 baseline 替换。RemoteJournalStream 检查起始 cursor 不倒退，忽略已覆盖重复记录，拒绝部分重叠，结合分页和 follow 补缺口。[snapshot baseline 消费](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/gateway/src/client/snapshot-stream.ts#L67-L94) [journal 游标与补偿](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/gateway/src/client/journal-stream.ts#L261-L391)

assistant-stream 使用连续 revision，snapshot 附带 activeAttempt，帮助客户端重连到当前实时状态。它不是把每个字块作为 journal 永久记录，而是针对尚在进行的展示提供一致视图。[active assistant attempt 快照](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/session-controller/src/assistant-stream.ts#L45-L102)

例如只是网络断开，Host 仍活着，新 baseline 能带回当前 attempt，之后继续接受连续变化。如果 Host 进程也退出，未结算的文本只存在旧 live 对象时，磁盘日志不能凭空补回它。两类故障对用户都像“断线”，恢复依据却不同。

协议错误也与网络载体丢失不同。游标重叠或非法 revision 可能需要终止当前订阅，不能无限吞掉再重连，否则页面展示会与真实历史悄悄偏离。

## 声明文件交付，需要独立事件

present 工具检查目标存在且为常规文件，收集待展示引用，在最终工具结果观察阶段写 `deliverables/presented`。

```typescript
ctx.on('tools/result', (exec, result) => {
  const delivery = pending.get(exec)
  pending.delete(exec)
  if (delivery === undefined || result.isError) return
  const { session, turn, files } = delivery
  session.append('deliverables/presented', {
    turn, callId: exec.callId, files,
  })
})
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/tool-present/src/index.ts#L100-L108)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

pending 以执行对象关联，结果错误时不声明。tool outcome 已确定后，观察通知不会反向改变它；observer 失败只警告，因此声明事件是否成功仍需要单独检查。[present 文件检查和声明](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/tool-present/src/index.ts#L70-L108) [结果观察的错误隔离](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/tools/src/index.ts#L1694-L1713)

这条声明表示“本会话展示这些文件”，不表示文件内容经过独立业务验收，也不表示文件已永久归档。路径引用所对应的文件还可能被之后修改；跨设备下载和长期分享需要额外的内容存储与访问能力。

排查交付时还要注意顺序。声明在 tools/result 通知中追加，可能先于 Loop 自己记录 tool/result。消费者按 seq 和 callId 关联，而不是假设所有成功结果之后才存在领域声明。

## 工作区变化先捕获基线，再确认本 Turn 的修改

workspace-changes 在 Turn 开始排队获取基线，相关工具执行前捕获路径，观察最终工具结果，在 turn-stopping 计算差异并记录。它尝试区分用户既有未提交变化与本 Turn 拥有的修改，而非简单展示当前 git diff。[基线、路径与结果观察](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/workspace-changes/src/recorder.ts#L128-L187) [owned delta 的计算](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/workspace-changes/src/recorder.ts#L303-L333)

例如用户发送任务前已经改了 README，Agent 只修改函数和测试，交付视图不应把 README 一起归为 Agent 成果。这个区分依赖有效基线、实际捕获和工具结果身份，不是仅看文件修改时间。

缺少基线、没有对应工具结果、超出支持范围或嵌套仓库路径，都可能限制记录。完整本地 Git 状态可以辅助比较，却不能从一次 Turn 的结果自动推导所有外部修改来源。

## 日志里的 changes 为什么不能恢复完整 diff

下面片段显示持久事实与具体记录分开：日志追加 workspace/changes 仅携带 turn，summary 和后续内容存在 records 索引。

```typescript
  if (sorted.length === 0 && state.recordedAfterSeq < 0) return
  const event = this.session.append('workspace/changes', { turn: state.turn })
  const kept = sorted.slice(0, this.env.maxFiles)
  this.records.set(event.seq, {
    summary: {
      turn: state.turn,
      cwd: this.cwd,
      files: kept.map(entry => entry.file),
      total: sorted.length,
      added: sorted.reduce((sum, entry) => sum + entry.file.added, 0),
      deleted: sorted.reduce((sum, entry) => sum + entry.file.deleted, 0),
      ...snapshot === undefined ? {} : { snapshot },
    },
    sources: kept.map(entry => entry.sources),
  })
  state.recordedAfterSeq = event.seq
}
```

[对应源码](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/workspace-changes/src/recorder.ts#L353-L369)。以上为原文片段，仅统一缩进，需结合完整实现阅读。

records 和临时 Git／捕获资源由 recorder 持有，dispose 清理索引与临时目录。重启后 Session 中可以保留 changes 事件，但旧 summary／sources 不一定仍可查询。[工作区记录的内存保存](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/workspace-changes/src/recorder.ts#L342-L369) [清理索引和临时资源](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/workspace-changes/src/recorder.ts#L242-L251) [官方覆盖与重启限制](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/deliverables/workspace-changes/README.md#L40-L60)

这是临时交付视图的生命周期，不应自动称为数据损坏。问题出在产品若承诺“永远可看旧 diff”，却只组合这项临时记录能力。要实现长期版本化产物，就需要另存内容、清单、hash 和来源版本。

## 怎样建立更准确的用户状态

可以把用户流程拆成几种可核验状态：消息已接纳、输入已消费、回合运行中、循环已结算、声明了交付文件、业务检查通过。网络连接状态另行展示，不把重连成功当作任务成功。

报告文件和工作区差异也应分开：前者是明确展示的文件引用，后者是一次 Turn 的修改记录。若需要下载，应确认当前文件版本；若需要审阅旧 diff，应确认对应临时或持久数据仍存在。

这些是基于现有协议和产物机制的产品设计建议，不是 DSH 当前界面全部已经提供的状态。良好界面应减少用户理解内部 seq 的负担，但其判断依据不能缺失。

## 优势、不足与技术心得

优势是命令身份、事实 journal 和实时状态分开，重连先建立 baseline，交付声明与工具结果可以关联，工作区比较也考虑原有修改。各类消费者有明确数据来源。

不足是 live 输出无法自然变成持久历史，文件引用不自动归档，workspace diff 依赖运行缓存。业务命令去重、跨设备产物、长期审阅和强访问控制还需要应用补充。协议测试通过也不等于真实网络和浏览器已验证。

我的技术心得是，交付不是最后一句回答，而是从执行事实到用户可访问结果的一条链。消息接纳、结果结算、产物声明、内容保存和权限访问都应有负责方。遗漏任一环节，用户就可能看到“成功”却拿不到结果。

此前 transport／assistant-stream 测试、V08 present 10 项和 V10 workspace 16 项支持选定本地路径。浏览器、真实网络和远端文件分发未实测。最后一篇将讨论怎样在版本升级和部署过程中保持这些状态语义。

---

研究基线：DeepSeek Harness `0.2.1-alpha.1`，提交 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。源码事实以该版本为准；文中的工程判断和改造建议另行说明。教学场景不代表真实模型业务实测。

源码与运行记录可从[证据索引](../appendices/evidence-index.md)和[验证附录](../appendices/validation.md)复核。本文引用此前同一提交的验证结果，本轮写作不将其重新计为新测试。

[专栏目录](README.md) · [上一篇](14-plugin-lifecycle.md) · [下一篇](16-deployment-evolution.md)
