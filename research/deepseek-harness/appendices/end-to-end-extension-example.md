# 企业任务扩展：端到端参考样例与实现边界

本说明复用[enterprise-harness](../examples/enterprise-harness/README.md)，将17—28篇的设计收敛到一个可验证的业务闭环。代码是本仓库的企业新增参考实现，上游内核固定为 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。已实现的是授权工单的 Host 执行闭环；完整企业 UI、SSO 与远端业务后端没有在本批新增。

## 1. 场景与数据契约

可信应用在完成用户认证与任务授权后，生产 `Subject { tenantId, actorId }` 和 `TaskSpec`。任务限定 Session、政策 revision、模型路由、attempt/token 上限、期限、ticketId 与 expectedVersion。相同工单编号可以属于不同租户，实际查询必须带可信 tenant 条件。

Agent 接到任务后只读取批准的工单，回答引用工单编号和版本。关闭工单由可信应用调用 `closeTicket`，该方法未注册为模型工具；这里把“模型研究结果”和“控制面业务提交”清楚分开，便于审阅、幂等与效果确认。

## 2. 文件与调用链

|文件|生产/消费责任|
|---|---|
|[ledger.ts](../examples/enterprise-harness/ledger.ts)|授权、预算保留、租户资源查询；事务写效果、receipt、audit|
|[platform.ts](../examples/enterprise-harness/platform.ts)|持有 ledger；按 live Agent object 绑定 grant；提供 backend 接入边界|
|[provision.ts](../examples/enterprise-harness/provision.ts)|预检查 → agents.create.setup → bind/policy/tool → commit 核验|
|[policy.ts](../examples/enterprise-harness/policy.ts)|restrict/guard、pre-step/request 再检查、Loop attempt reservation、审计|
|[ticket-tool.ts](../examples/enterprise-harness/ticket-tool.ts)|schema 校验 → current grant → await readTicket → signal/current 再检查|
|[enterprise-example.spec.ts](../validation/enterprise-example.spec.ts)|mock LLM 驱动真实 Loop，并检查授权、重试、取消与事务|

创建完成之后，应用持有 `AgentHandle`，提交输入并观察 Session。工具结果经 ToolRuntime 进入下一次模型请求；回答不是业务写入证明。控制面若调用 `closeTicket`，需取得 `CloseReceipt` 才确认工单效果，finally 中等待 Agent dispose。

## 3. 实际复现

在研究仓库根执行；前置条件是固定 checkout、已安装 dependencies 与 vendor declarations。Node 版本使用24.19.0。

```sh
node research/deepseek-harness/validation/enterprise-example.mjs typecheck
node research/deepseek-harness/validation/enterprise-example.mjs build
node research/deepseek-harness/validation/enterprise-example.mjs test
node research/deepseek-harness/validation/supplementary-pack-smoke.mjs
```

前三步检查 strict types、5个 ESM 模块和16项 compiled integration tests。pack smoke 自动生成忽略目录里的 tarball，核对 exports 文件存在，再从解包目录导入 `./ledger`，验证重复写入取得同一 receipt、重开数据库后 receipt 仍有效、只产生一次业务审计。它没有导入其余需要 DSH peers 的插件入口，不能作为独立安装整个 Harness 的证据。

## 4. 如何继续接入界面与业务系统

[21篇](../articles/21-fullstack-plugin-development.md)用现有设置卡片说明 package → Client graph → Remote → controller → Slot → React。企业可新增查询服务与面板，但必须配套 typed descriptor、真实业务 schema 和请求身份，不能把 agent-loop namespace 改个显示名称就冒充新接口。

[22篇](../articles/22-sdk-acp-web-integration.md)提供 SDK 集成教学代码。默认 SDK/ACP 创建路径没有自动加入 preset；采用企业 provisioning 时，必须明确改造其创建入口，或在自建可信 Host API 中调用 `createEnterpriseAgent`。本批没有声称现有 SDK 已自动使用这个企业样例。

Skill 可按[18篇](../articles/18-skill-instruction-loading.md)注册 SOP，PTC 可按[24篇](../articles/24-ptc-program-execution.md)提供受控 bindings。参考企业 policy 使用 native mode；不能未经回归就宣称 PTC、Workflow children 及每个 direct LLM 调用都继承同一授权/预算。

## 5. 故障与退出验收

样例实测覆盖伪造 Subject、相同 id 的租户隔离、未批准资源、Scope-local rogue tool、下游 await 中撤销、retry budget、deadline cancel，以及事务 audit 故障导致业务和 receipt 一起 rollback。具体测试和结果见[验证记录](../validation/supplementary-articles-validation.md)。

真实 connector 替换 `platform.readTicket` 时，再补凭据轮换、网络 deadline、输出大小、来源信息和响应后授权复核。远端写入要定义服务器幂等和查询协议，断线结果可能 unknown；本地 SQLite 的事务原子性不能直接推广到远端 HTTP。

端到端设计的实用价值，是使每个批准、接纳、工具结果、业务效果和退出都能找到其生产者与观察者。扩展可以逐步增加，但完成事实应从第一版就明确。
