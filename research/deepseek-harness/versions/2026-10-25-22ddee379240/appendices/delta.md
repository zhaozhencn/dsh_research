# 从 alpha.1 到 rc.3：插件开发迁移

## 1. 版本范围与证据口径

旧 SHA `5badb15009ae1756c3afe0ae0cef1faafc290ccc`（0.2.1-alpha.1），新 SHA `22ddee3792402c3e70ec5f86a63c3e3e895a2f60`（0.2.1-rc.3）。2026-10-25 在线确认官方默认 master HEAD；提交本身时间为 2026-10-23。旧提交是祖先，中间 3,198 commits。tracked 14,208 → 19,188；workspace 341 → 386，按包名新增 46、删除 1。

本轮以插件开发作为复核范围。全量 files/commits/impact 只是调查材料；manifest 依赖闭包不等于运行期 DI/事件影响。新正文从实际调用链重建，旧 29 篇正文和日志不覆盖。旧 evidence 的机械结果：identical-text 45、reanchored-identical-text 35、changed 65、missing 4；149 条全部保留 pending，不能作为已审阅的 149 条当前结论。

## 2. 必须迁移的开发写法

|主题|旧研究中的写法/结论|当前结论与迁移|证据|
|---|---|---|---|
|模型策略|route-policy 在 agent/request 改 provider/model|使用 agent.model.select；Step 已捕获后变更下个 Step 生效；重试保持捕获值|[E05](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/agent.ts#L276-L310) [E07](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/agent.ts#L606-L651) [E28](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-alpha.4/session-model-selection/guide.md#L1-L28)|
|工具执行|dsh-tools 承担 Native/PTC 模式|挂 Native 或 PTC executor；删 tools.mode/maxParallelSubCalls；PTC 子调用限制迁到其 executor|[E09](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tool-executor-native/src/index.ts#L1-L35) [E10](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/executor.ts#L20-L102) [E27](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/index.ts#L99-L115)|
|条件工具|在 system-prompt/assemble 筛工具|registration.when + ResolvedToolSet；presentation 不再带 tools|[E03](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/contracts.ts#L104-L137) [E04](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/index.ts#L230-L300) [E29](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-rc.2/conditional-tools/guide.md#L1-L25)|
|热更/MCP 重注册|相同名字可被误认为继续执行同一工具|已准入集合比对定义与注册身份；替换/撤销使未启动调用 UNKNOWN_TOOL|[E04](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/index.ts#L230-L300)|
|投影注册|register 返回同步 disposer，按 key 读|await register 得 private handle；handle.stateOf；异步 apply 返回 void；旧 callable 仅兼容|[E12](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/session/session-projection/src/index.ts#L302-L430) [E37](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/session/session-projection/README.md#L62-L106)|
|模型投影归属|入口/API 负责选择状态|AgentLoop owns projection 和 Agent.model；普通 consumer 不再另注册其定义|[E28](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-alpha.4/session-model-selection/guide.md#L1-L28)|
|Session 创建|setup 与创建公告顺序不能直接沿用|Session 公告 → setup → Agent 发布；公告内禁止写 store-owned Session|[E21](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/index.ts#L616-L651) [E22](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-rc.2/session-store-writes/guide.md#L1-L25)|
|Remote 权限|原研究主要讨论本地身份、企业层新增授权|已有 Peer principal、Remote resources、policy；企业身份与业务租户仍需实现|[E13](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/api/gateway/src/index.ts#L783-L825) [E14](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/api/remote-access/src/index.ts#L160-L227) [E19](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/defensive-patterns/remote-and-api.md#L9-L64)|
|插件兼容|看 DSH peers 判断|有自有 engines.dsh 时以其单独判断；缺省才回退 peers；拒绝字段 requirements|[E11](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/boot/app-boot/src/plugin-compatibility.ts#L52-L101)|
|Client 依赖|泛称 client dependencies 容易误导|分开 service inject、信息性 dsh.client.inject、值模块 external 与 ./client artifact|[E16](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/client/modules/src/index.ts#L889-L919) [E17](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/client/AGENTS.md#L73-L104)|
|普通 fork|可能沿用父子关系追踪|新普通 fork 不写 parentSession；subagent 才保留直接创建者；V4 名称相同不保证旧 reader 可读|[E35](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/session/src/types.ts#L83-L101) [E36](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-rc.3/independent-session-forks/guide.md#L1-L23)|

旧 route 示例对照：[alpha.1 prepareRequest](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-loop/src/agent.ts#L547-L686)；当前拒绝检查见上表。此处是明确历史对照，不能用于当前正文依据。

## 3. 保留的原则与仍存在的差异

注册属于 effect，waterfall 需要 next 委托，模型可见内容需要日志依据，外部副作用不能盲重试。这些原则在新规则和执行 pipeline 中重新确认。持久选择也不会因策略卸载自动撤回。[E26](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/AGENTS.md#L129-L149) [E32](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/pipeline.ts#L254-L290)

仍有一项官方文档与真实接口不一致：当前 architecture 的接缝表提到 Persistence export，但 `SessionPersistence` 抽象类仍只有 create/open/flush/stat/list，不能据此实现不存在的 export 方法。集成以该提交真实接口及相邻导出能力为准。本批未实现新的持久后端。[E34](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/session/session-persistence/src/index.ts#L144-L213)

未被本轮深读或实测的性能、各平台 sandbox、Team、SSH/PTC runtime、真实模型及企业示例，一律保留为待复核；未检出同名字段不单独作为“功能删除”证据。

## 4. 原有文档如何继续使用

|原内容|本轮当前替代入口|处理|
|---|---|---|
|[01 宏观架构](../../../01-architecture.md)、[02 源码运行](../../../02-runtime-source.md)|[当前架构](../01-architecture.md)、[当前运行链](../02-runtime-source.md)|旧篇保留 alpha.1；本批聚焦扩展相关机制|
|[03 扩展实践](../../../03-extension-practices.md)|[当前开发指南](../03-extension-practices.md)|两个插件已迁移；不要复制旧路由写法|
|[04 企业实践](../../../04-enterprise-harness-practices.md)|当前开发指南的 Remote/connector 章节|旧企业实现未迁移，原则与当前原生权限分开|
|专栏 01、03、04、07、12|当前运行链与模型/工具章节|scope、Step 准入和执行器按新版解释|
|专栏 17、19、20、21、27、28|当前架构、契约矩阵、开发指南|创建顺序、投影、兼容、Remote 与构建面按新版解释|
|专栏 18、23、24、25、26|工具准入与权限变化可作为迁移线索|未重跑其全部 runtime，不宣称整篇已升级|
|其他专栏与所有历史图片|仍是固定 alpha.1 的研究|原样保留；不把未复核部分挂新 SHA|

## 5. 升级执行顺序（工程建议）

1. 为目标源码独立安装依赖；验证插件 package exports、peers 和 engines.dsh。
2. 将模型选择提前到 Step 准备前；补 executor，并移除旧 tools 配置与 assembly 工具过滤。
3. 迁移投影 await/handle 和创建时写入位置；检查 Remote principal/资源列表与 grant 失效通知。
4. 运行正常两 Step、非法输入、取消、撤销旧工具和旧路由拒绝回归；检查业务幂等与权限变更。
5. 用副本数据验证 reader/writer、恢复与普通 fork；不要在旧 reader 无验证时共享新的 V4 目录。
6. 构建并在临时 home 中安装真实包，检查 dump-config 与运行激活，再做 UI、网络和目标平台验收。

本批实际完成的是 1—4 中参考扩展与选定上游契约测试，业务系统、持久目录迁移和发布安装需要下一层验证。完整结果见[本批验证](validation.md)。
