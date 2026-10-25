# 当前源码证据索引

基线 `22ddee3792402c3e70ec5f86a63c3e3e895a2f60`。重要结论采用源码事实、官方说明、运行验证、分析推断、改造建议五类；未实际运行的能力不标为运行验证。所有源码片段从 Git 对象计算 hash，完整数据见 [evidence.json](evidence.json)。

|ID|性质|结论与定位|
|---|---|---|
|E01|官方说明|[E01 · profile、bundle、支持的启动入口与组合顺序](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/architecture.md#L9-L68)|
|E02|官方说明|[E02 · 当前包版本、Node 和 packageManager 声明](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/package.json#L1-L16)|
|E03|源码事实|[E03 · 条件工具与 ResolvedToolSet 声明](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/contracts.ts#L104-L137)|
|E04|源码事实|[E04 · 工具查询、条件准入与 registration 身份复核](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/index.ts#L230-L300)|
|E05|源码事实|[E05 · preStep 捕获模型并准入工具、组装和清理](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/agent.ts#L276-L310)|
|E06|源码事实|[E06 · Turn 消费 PreparedStep 与 finally 释放 toolSet](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/agent.ts#L335-L390)|
|E07|源码事实|[E07 · prepareRequest 拒绝 deprecated hook 变更路由或 effort](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/agent.ts#L606-L651)|
|E08|源码事实|[E08 · modelSelection fold、AgentModel 与切换提示](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent/src/model-selection.ts#L17-L174)|
|E09|源码事实|[E09 · NativeToolExecutor 描述与 batch 委派](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tool-executor-native/src/index.ts#L1-L35)|
|E10|源码事实|[E10 · ToolBatchInput、Result 与 executor 排空义务](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/executor.ts#L20-L102)|
|E11|源码事实|[E11 · engines.dsh 优先与 DSH peer 回退](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/boot/app-boot/src/plugin-compatibility.ts#L52-L101)|
|E12|源码事实|[E12 · callable thenable、await acquire、handle 与释放](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/session/session-projection/src/index.ts#L302-L430)|
|E13|源码事实|[E13 · 非 owner 调用先授权，再解析 receiver](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/api/gateway/src/index.ts#L783-L825)|
|E14|源码事实|[E14 · policy effect、失效通知和逐资源判定](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/api/remote-access/src/index.ts#L160-L227)|
|E15|源码事实|[E15 · 锁内配置验证、原子写盘、reconcile 与恢复](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/boot/config-editor/src/index.ts#L80-L153)|
|E16|源码事实|[E16 · 从实际插件 manifest 定位 Client bundle](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/client/modules/src/index.ts#L889-L919)|
|E17|官方说明|[E17 · Client 共享模块、公开构建环境与 DI 区分](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/client/AGENTS.md#L73-L104)|
|E18|官方说明|[E18 · profile 范围、插件管理、安装和 restart-required](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/boot/plugin-manager/README.md#L31-L79)|
|E19|官方说明|[E19 · 业务 Remote 独立 service、caller 来源与完整资源](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/defensive-patterns/remote-and-api.md#L9-L64)|
|E20|官方说明|[E20 · typed 输入、canonical 输出、取消、背景作业与策略](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/cookbook/adding-a-tool.md#L9-L84)|
|E21|源码事实|[E21 · Session 公告、setup、Agent 发布及失败清理](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/index.ts#L616-L651)|
|E22|官方说明|[E22 · store-owned Session 写入与创建顺序变化](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-rc.2/session-store-writes/guide.md#L1-L25)|
|E23|源码事实|[E23 · Agent Model API 的可用性验证归调用者](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent/src/runtime-types.ts#L53-L72)|
|E24|官方说明|[E24 · 构建、typecheck、验证命令及范围](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/AGENTS.md#L74-L121)|
|E25|官方说明|[E25 · 接缝选择、Conversation 与应用接入](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/cookbook/extension-cookbook.md#L5-L132)|
|E26|官方说明|[E26 · ESM、effects、waterfall、logged 与 capability roles](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/AGENTS.md#L129-L149)|
|E27|源码事实|[E27 · 移除 tools.mode 及 executor 选择](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/index.ts#L99-L115)|
|E28|官方说明|[E28 · 模型选择、恢复与 effort 的迁移说明](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-alpha.4/session-model-selection/guide.md#L1-L28)|
|E29|官方说明|[E29 · 条件准入、组装接口与未知工具行为](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-rc.2/conditional-tools/guide.md#L1-L25)|
|E30|源码事实|[E30 · 绑定调用后再提交系统提示和接纳输入](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/agent.ts#L430-L475)|
|E31|源码事实|[E31 · 取消测试的真实 runtime 装配和结算意图](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/tests/cancel.spec.ts#L1-L99)|
|E32|源码事实|[E32 · 融合信号、重新解析定义并等待 body](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/pipeline.ts#L254-L290)|
|E33|源码事实|[E33 · post-execute、最终冻结与 result 通知](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/pipeline.ts#L327-L394)|
|E34|源码事实|[E34 · Persistence 当前真实方法集合](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/session/session-persistence/src/index.ts#L144-L213)|
|E35|源码事实|[E35 · Session 当前逻辑版本为 V4](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/session/src/types.ts#L83-L101)|
|E36|官方说明|[E36 · 普通 fork 独立及旧 reader 拒绝风险](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-rc.3/independent-session-forks/guide.md#L1-L23)|
|E37|官方说明|[E37 · 投影 retained handle 与弃用兼容行为](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/session/session-projection/README.md#L62-L106)|
|R01|运行验证|两个编译扩展的类型、构建与 8 项真实 Loop 集成通过|
|R02|运行验证|13 个选定上游测试文件 284 项通过|
|A01|改造建议|Remote 与 Tool consumer 共用业务授权领域服务，并分别定义外部提交与 Session 结算|

外部在线访问：2026-10-25 打开官方 GitHub 仓库，并以 git ls-remote 发现默认分支；后续阅读固定提交内源码和官方说明。官方 master 还在变化，报告不会在验证中途自动追随新 HEAD。

旧 evidence-status.json 的全部 149 条记录仍为机械 pending 候选；当前 evidence.json 另行重建，不把文本相同冒充语义复核。
