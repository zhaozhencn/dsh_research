# 第三篇：从最小插件到可交付扩展

本篇面向已经能读 TypeScript、准备为 DSH 开发业务扩展的工程师。以 `22ddee3792402c3e70ec5f86a63c3e3e895a2f60` / `0.2.1-rc.3` 为唯一当前基线，提供接口选择、两个可运行插件、前后端接入与升级验收。这里的“最佳实践”分成官方开发规则、已测试的源码行为和带前提的工程建议；不承诺预稳定接口跨版本兼容。

整体开发路径是：定义能力和资源身份，选扩展点，在正确 scope 注册，通过同一 Step 的工具集执行，明确结果的消费面与退出责任，最后验证真实安装产物。下面从最小工具进入这条路径，再扩展到模型策略、UI 和企业 connector。

## 1. 用需求选择扩展点

|开发目标|当前首选入口|关键约束|
|---|---|---|
|增加模型工具|`ctx.tools.register(defineTool(...), { when })`|schema、canonical output、signal 和注册所有权|
|限定一个 Agent 的能力|在 setup/`agent.ctx` 挂插件；必要时 `restrict`|scope 是能力继承；企业授权还需业务校验|
|按模型或状态启用工具|registration 的 `when(context)`|Step 准备时计算一次，后续声明和执行共用集合|
|选择 provider/model/effort|准备 Step 前 `agent.model.select(selection)`|选择持久化；已准备 Step 和重试不变|
|改写本次接纳内容|`agent/pre-step` 或 prompt contributions|保留 `startsRequestSeries`；模型可见内容需入日志|
|工具审批或拒绝|`tools/pre-execute`；最终不变量用 `guard`|后续 listener 不能推翻 guard 的拒绝|
|限时与执行观测|`tools/execute` around-wrapper|融合原取消、finally 恢复 signal、排空 body|
|修改结果/附加上下文|`tools/post-execute`|content 与 value 的影响分别考虑|
|最终审计|`tools/result`|观察冻结权威结果；不承担异步业务提交|
|切 Native/PTC|选择 executor 插件|不能再配置 `dsh-tools.mode`|
|持久派生状态|await projection registration，domain 持有 handle|同步 fold、stateVersion、handle 生命周期|
|开放业务 Remote|独立 service 的具体 `@Remote` 方法|generated codec、Peer caller、全部涉及资源|
|新增页面/Chat 展示|Client 插件 + Slots/Conversation|Host/Client 分编译、持久卡片数据、重连|

表中工具与模型行为已由本次测试复核；UI、真实服务与安装仍需对应环境验收。接口证据集中见 [E03 · 条件工具与 ResolvedToolSet 声明](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/contracts.ts#L104-L137) [E07 · prepareRequest 拒绝 deprecated hook 变更路由或 effort](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/agent.ts#L606-L651) [E10 · ToolBatchInput、Result 与 executor 排空义务](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/executor.ts#L20-L102) [E19 · 业务 Remote 独立 service、caller 来源与完整资源](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/defensive-patterns/remote-and-api.md#L9-L64) [E20 · typed 输入、canonical 输出、取消、背景作业与策略](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/cookbook/adding-a-tool.md#L9-L84) [E25 · 接缝选择、Conversation 与应用接入](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/cookbook/extension-cookbook.md#L5-L132)。

## 2. 先做一个有完整数据契约的工具

[sum-tool/index.ts](examples/sum-tool/index.ts) 是独立 ESM 包，编译文件位于同包 `lib/index.js`。插件暴露 Config.enabled 并声明 `inject = ['tools']`；下面是核心注册片段，完整 imports 和配置以文件为准：

```ts
ctx.tools.register(defineTool({
  name: 'research_sum',
  description: 'Return the sum of two finite numbers.',
  parameters: {
    a: { type: 'number', required: true },
    b: { type: 'number', required: true },
  },
  output: {
    schema: { type: 'number' },
    render: (_args, value) => [{ type: 'text', text: String(value) }],
  },
  isConcurrencySafe: () => true,
  async execute(args, exec) {
    exec.signal.throwIfAborted()
    const value = args.a + args.b
    if (!Number.isFinite(value)) throw new RangeError('sum must be finite')
    return value
  },
}), { when: () => config.enabled })
```

这段是本报告示例代码。`defineTool` 从 parameters 推导 execute 参数类型，并校验模型输入；业务仍需校验 DSL 表达不了的约束。加法返回 number，render 负责文本表示。若改为写工单，canonical output 应包含 `operationId`、业务结果与状态字段，不能只返回“创建成功”让调用者解析中文。raw JSON-Schema tools 的输入校验责任与 typed helper 也不同，不应混为一谈。[E20 · typed 输入、canonical 输出、取消、背景作业与策略](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/cookbook/adding-a-tool.md#L9-L84)

`when` 解决该 Step 是否可调用；业务授权仍在实际资源操作处执行。比如工单归属在异步请求期间发生变化，旧的准入成功不能替代提交前检查。加法没有共享状态，才声明并发安全；网络调用是否 read-only、是否幂等、是否可并发，应依业务后端保证决定。

注册归属调用 Context 的 Fiber，卸载时自动撤销。带取消的资源操作必须把 `exec.signal` 传给支持它的客户端，或映射到进程终止/连接关闭；不能只在调用开头检查一次。这个最小算术例只需要同步计算前检查，不提供长请求取消模板。

本次测试证明启用时 `2+3` 的 `5` 进入真实 Loop 第二次请求，错误参数得到 `INVALID_ARGS`，禁用时模型不见 schema 且伪造调用得到 `UNKNOWN_TOOL`。还验证了解析出 toolSet 后卸载插件，旧集合无法执行被撤销的工具。详见[测试文件](validation/extensions.spec.ts)。

## 3. 程序调用与模型调用共享准入

程序需要直接调条件工具时，必须先取得并最终释放 Step 类似的集合。下面是当前 API 的完整调用形态；`agent` 已由调用者持有，缺模型选择时应报告配置错误：

```ts
const selection = agent.model.current()
if (selection === undefined) throw new Error('No model selected')
const toolSet = await ctx.tools.resolve({
  agent, modelSelection: selection, signal,
})
try {
  const result = await ctx.tools.execute({
    agent, signal, toolSet,
    calls: [call],
  })
  // Consume result.results; this is outside a committed model step.
} finally {
  toolSet.dispose()
}
```

这是集成说明片段，`ctx`、`agent`、`signal`、`call` 来自调用者。不要为普通服务请求伪造 `log: {turn, step}`；只有已提交模型 Step 才提供它。批次返回 `results`、`additionalContexts`、`concluded`，调用方分别处理结果、后续上下文和终止标记。若自己编写 executor，必须保持每个输入调用都有按模型顺序的结算，取消后等待已启动任务释放。[E10 · ToolBatchInput、Result 与 executor 排空义务](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/tools/src/executor.ts#L20-L102)

PTC 模式会把已准入工具映射为程序方法，并取得最终 canonical value。纯工具一般无需额外集成 PTC；自定义 program runtime、并发子调用和后台任务则有独立生命周期，不能把 Native 成功当作 PTC 已验收。[E20 · typed 输入、canonical 输出、取消、背景作业与策略](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/cookbook/adding-a-tool.md#L9-L84)

## 4. 迁移模型策略：在准备 Step 前选好

旧示例依赖 `agent/request` 替换 provider/model。当前源码保留事件兼容执行，却明确拒绝改变 route 和 reasoning effort；因此应该迁移策略职责，不能仅修改导入版本。[E07 · prepareRequest 拒绝 deprecated hook 变更路由或 effort](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent-loop/src/agent.ts#L606-L651)

[route-policy/index.ts](examples/route-policy/index.ts) 采用一个范围清晰的策略：在 `agent/created` 选择配置指定的路线，之后允许用户显式选择改变它。listener 只服务该挂载 Context 可见的 Agent：

```ts
ctx.on('agent/created', ({ agent }) => {
  agent.model.select({ provider: config.provider, model: config.model })
})
```

在 Agent setup 挂载它，便只影响这个 Agent；部署级挂载会影响该 Context 可见的新建/恢复 Agent。给已有 Agent 挂上此插件，不会补发 created；若要修改已有会话，验证路由后直接调用 `agent.model.select()`。这是一次持久选择，不是每个 attempt 自动重新选路，更不是 provider 熔断器。

可选的 `installModelSelection(agentCtx)` 负责切换提示，当前不再接受 selection 参数。自定义组合应在 unpublished setup 内按需装一次；已配置该功能的宿主不要重复安装。示例插件不再自行重复装它。完整的路由发现、用户权限、价格或健康策略由业务实现，`select()` 本身不替你验证这些决策前提。[E08 · modelSelection fold、AgentModel 与切换提示](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/core/agent/src/model-selection.ts#L17-L174)

本次 scope 测试中，请求模型依次为 `policy → base → policy`：目标 Agent 使用策略路线，另一个 Agent 保持 base，策略卸载后目标 Agent 仍保留已记录的选择。另一用例在 pre-step 内才选新路线，实际为第一 Step base、工具续接 Step policy。这是持久状态和 Step 捕获的两个不同效果。

若要求所有请求永远走固定部署路线，应明确用户切换的权限与会话恢复策略，在正常入口预先设置；不要把 created 示例当作禁止用户切换的安全控制。programmatic resume 还会优先恢复已记录选择，仅传 AgentOptions 不一定覆盖历史，应在 setup 根据业务策略显式选择。[E28 · 模型选择、恢复与 effort 的迁移说明](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/upgrade-guide/v0.2.1-alpha.4/session-model-selection/guide.md#L1-L28)

## 5. 从工具扩展到前后端插件

一个双端包至少需要 Host 入口、独立 Client 产物、`dsh.client` 声明和 `./client` export。Host 扫描实际 Loader 所挂载包的 manifest；Client 不能 import Node-only service 实现，类型尽量 `import type`，共享值只通过批准的模块表。[E16 · 从实际插件 manifest 定位 Client bundle](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/client/modules/src/index.ts#L889-L919) [E17 · Client 共享模块、公开构建环境与 DI 区分](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/client/AGENTS.md#L73-L104)

|声明|表达什么|不能替代什么|
|---|---|---|
|Host `inject`|Host services 就绪条件|Client bundle 依赖|
|Client Cordis `inject`|Client services 激活条件|浏览器同步模块装载|
|`dsh.client.inject`|包名信息，用于展示/HMR 等|激活或 apply 顺序|
|`dsh.client.external`|共享值模块的实际请求|普通业务依赖声明|
|`exports['./client']`|可服务的编译产物入口|源文件本身或静态类型检查|

共享平台模块已由 baseline 提供，不重复列入 external；其他第三方库可以私有打包，但不能复制需要单实例身份的 runtime。Client 资源图片也要覆盖 `exports['./assets/*']` 与 files。构建时读取的 `DSH_CLIENT_*` 全部是公开产物内容，密钥必须留在 Host credentials 路径。[E17 · Client 共享模块、公开构建环境与 DI 区分](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/client/AGENTS.md#L73-L104)

界面展示先明确数据来源：纯请求回执走 Remote，持久业务状态走领域事件/投影，模型瞬时输出走 stream。用 Slots 添加界面，用 Conversation node/renderer 添加 Chat 业务节点；不要直接把 JSX 分支塞进通用 session controller。重连和回放需验证卡片来自日志或稳定投影，而不是上一次页面内存。当前新投影用私有 handle 提供业务 reader，其他插件 inject 领域 service 获取数据。[E12 · callable thenable、await acquire、handle 与释放](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/session/session-projection/src/index.ts#L302-L430) [E25 · 接缝选择、Conversation 与应用接入](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/cookbook/extension-cookbook.md#L5-L132)

## 6. 给 Remote 能力完整命名资源

当前 Gateway 具有方法和事件访问控制，企业扩展应接入它。新增业务能力创建独立 service，把 `@Remote` 标在真正执行能力的具体方法上；Client 类型来自 Typert 生成结果。Remote caller 从 invocation 取得，不能从 JSON 参数传入。[E13 · 非 owner 调用先授权，再解析 receiver](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/api/gateway/src/index.ts#L783-L825) [E19 · 业务 Remote 独立 service、caller 来源与完整资源](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/defensive-patterns/remote-and-api.md#L9-L64)

访问检查发生在 receiver lookup 之前。资源列表来自 `@Remote({ resources })` / `@RemoteScope` 及自动 lookup 解析；遗漏某项资源就不会自动检查它。聚合列表须对每条记录调用业务允许性过滤，事件则按所声明资源决定整条发送或丢弃。`remoteAccess.registerPolicy(kind, policy)` 提供 principal 种类的角色与 binding；grant、撤权、模式或过期变化要调用 invalidate 使打开的访问快照更新。[E13 · 非 owner 调用先授权，再解析 receiver](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/api/gateway/src/index.ts#L783-L825) [E14 · policy effect、失效通知和逐资源判定](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/api/remote-access/src/index.ts#L160-L227)

**工程建议：**把企业身份映射、资源归属和工具 connector 授权接在同一个业务领域服务，分别给 Remote 与 Tool consumer 使用。Remote 允许一次方法不代表工具有权操作另一个工单；owner 本身是可信主体，也不能据此宣传多租户完全隔离。本批只运行上游 RemoteAccess host 单测，未做完整网络 Gateway/企业 SSO E2E。

## 7. 配置和包交付

两个示例都有独立 package.json、Config 和编译入口。manifest 固定 `engines.dsh: '0.2.1-rc.3'`，peer 指向相同 DSH/Cordis 版本；这表达本轮验证范围。外部插件不要使用 `workspace:*` 作为引擎范围，也不要复制官方 monorepo 所有私有构建细节。[E11 · engines.dsh 优先与 DSH peer 回退](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/boot/app-boot/src/plugin-compatibility.ts#L52-L101)

安装与激活分别检查：先在目标 profile 安装包，再用 patch 插入 entry；单包插件不因 `pnpm add` 自动成为 bundle。bundle 则通过 `dsh.bundle` 声明 patch，profile 选择它才进入组合。patch 的 config 为整体替换，需要完整保留期望配置。先用 `--dump-config` 检查最终树，随后验证运行状态。[E01 · profile、bundle、支持的启动入口与组合顺序](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/docs/architecture.md#L9-L68) [E18 · profile 范围、插件管理、安装和 restart-required](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/boot/plugin-manager/README.md#L31-L79)

Plugin Manager 在无 HMR 的 profile 上可能返回 `restart-required`；安装完成不能当作运行树已切换。配置写入器还会拒绝被 home/CLI overlay 覆盖、无法产生预期结果的编辑。更新失败中的文件恢复与服务恢复应分别检查，外部业务副作用要另行处置。[E15 · 锁内配置验证、原子写盘、reconcile 与恢复](https://github.com/deepseek-ai/deepseek-harness/blob/22ddee3792402c3e70ec5f86a63c3e3e895a2f60/packages/boot/config-editor/src/index.ts#L80-L153)

## 8. 本地复现与升级验收

从本研究仓库根目录运行，前提是目标源码在 `.sources/deepseek-harness-2026-10-25`。源码下载、冻结依赖、原生模块与 vendor 声明的完整准备命令见[示例说明](examples/README.md)。

```sh
node research/deepseek-harness/versions/2026-10-25-22ddee379240/validation/check.mjs typecheck
node research/deepseek-harness/versions/2026-10-25-22ddee379240/validation/check.mjs build
node research/deepseek-harness/versions/2026-10-25-22ddee379240/validation/check.mjs test
```

预期分别为严格检查退出 0、两个 ESM 插件产物生成、8 项集成用例通过。测试使用编译插件与 fixed-SHA 源码 aliases，真实 Cordis、Session、Loop、ToolExecutor 和 pipeline，模型由可控 adapter 供流。原生构建单独完成，全部日志保留于 validation。

|交付面|最小验收|本次证据|
|---|---|---|
|工具|正常两 Step、错误输入、禁用和旧集合撤销|新集成用例已跑|
|模型选择|scope、旧 hook 拒绝、下一 Step 生效、卸载后状态|新集成用例已跑|
|取消/清理|prefix 结算、idle、handle/Fiber dispose|新集成用例与上游选定用例已跑|
|投影/兼容|await registration、handle、兼容声明|选定上游用例已跑|
|业务 Remote|权限绑定的基本决策|上游 host 单测已跑；网络 E2E 未跑|
|前端|真实 bundle、slot、重连/回放|仅源码与官方开发规则复核|
|外部服务/发行|真实 provider、tarball consumer、profile 激活、跨平台|本批未验证，发布前补齐|

本次 284 项上游测试与 8 项自编测试分开记录，不与旧版 1,520 项累加；重跑也不重复计数。逐条升级影响和旧文章阅读指引见[版本差异](appendices/delta.md)。

插件开发中最值得建立的习惯是：每个注册写清所属 scope，每个异步点写清取消与晚到结果处理，每个模型可见值写清日志来源，每个外部写入写清业务确认，每个产物写清真正消费它的入口。这样，从小工具扩展到私有工作台时，新增复杂度仍能沿既有接口验证。
