# 企业工单助手参考实现

适用上游 SHA `5badb15009ae1756c3afe0ae0cef1faafc290ccc`；Harness `0.2.1-alpha.1`、Cordis `4.0.5-alpha.1`、Schemastery `3.18.5-alpha.1`。实测 Node `24.19.0`、pnpm `11.7.0`、TypeScript `6.0.3`、Vitest `4.1.8`，平台为本机 macOS arm64。

设计分析见[企业开发实践](../../04-enterprise-harness-practices.md)。本例演示可信任务授权、Agent 对象绑定、窄参数工具、持久调用准入预算、协作式取消，以及本地数据库中的幂等业务写入。它不实现 SSO，也不直接连接生产系统。

## 文件与契约

|文件|用途|
|---|---|
|[platform.ts](platform.ts)|服务 `ctx.enterprisePlatform`、身份绑定、后端接缝和清理|
|[policy.ts](policy.ts)|独立 policy 插件：restrict／guard、准入、模型路由与预算、分阶段审计|
|[ticket-tool.ts](ticket-tool.ts)|独立工具插件：`enterprise_ticket_read(ticketId)`|
|[provision.ts](provision.ts)|由可信入口调用，先授权，再在 setup 组装，发布 commit 复核|
|[ledger.ts](ledger.ts)|SQLite 应用账本；不是 SessionPersistence provider|
|[package.json](package.json)|一个 ESM 包，以 subpath 导出各插件和辅助模块；不打包 peer runtime|
|[cordis.patch.yml](cordis.patch.yml)|平台服务的 profile 接线骨架，正式入口插件另行提供|

`TaskSpec` 来自已经通过认证和资源授权的控制面。它绑定 tenant、actor、Session、policy revision、精确工单、模型路由、调用次数、单次输出上限、最长一天的有效期及可选写权限。模型只能输入 ticketId，不能改变绑定的主体和目标资源。

工单工具始终只读。`closeTicket()` 是可信应用命令，要求任务已明确获得 `canClose`，没有向模型暴露，也不由模型回复自动触发；业务效果、回执和审计在同一数据库事务中提交。远端业务系统需要另外实现幂等协议和核对。

## 从研究工作区复现

前提：固定 SHA 的独立 checkout 和依赖已就绪，vendor 声明已按原研究生成。缺少依赖时按[原示例准备说明](../README.md)准备；不要更改 checkout 版本来凑测试。

```sh
node research/deepseek-harness/validation/enterprise-example.mjs typecheck
node research/deepseek-harness/validation/enterprise-example.mjs build
node research/deepseek-harness/validation/enterprise-example.mjs test
```

从研究仓库根目录运行。每个命令可以在 mode 后传入 checkout 的绝对路径。typecheck 使用原基线的严格配置和 vendor 声明；build 将五个 TypeScript 模块编译到 [lib](lib/platform.js)，保留 bare peer imports；test 加载编译产物并使用源码 aliases 将运行包指向同一 checkout。

预期：typecheck／build 退出 0，测试 **16 passed**。真实 DSH Loop 完成“模型调用工单工具 → 规范结果进入后续请求”；同时验证 tenant／资源约束、scope guard、撤销、额度耗尽、同 Step 重试、截止取消、Handle 释放、数据库重开和业务幂等。全部使用临时或内存数据库，无模型凭据，无真实网络。

日志：[类型检查](../../validation/enterprise-typecheck.log)、[构建](../../validation/enterprise-build.log)、[测试](../../validation/enterprise-tests.log)；[运行台账](../../validation/enterprise-runs.json)记录退出码、基线与验证范围。typecheck 日志为空代表退出 0 且没有诊断，build 本身不替代 semantic typecheck。

## 可信入口插件中的调用示例

以下代码放在通过认证／授权的应用处理逻辑中。示例主体是演示值，不是 token 校验代码；任务 ID、Session ID 由服务器生成，并先写入企业任务数据库。

```ts
import { randomUUID } from 'node:crypto'
import { createEnterpriseAgent } from 'research-enterprise-harness/provision'
import { createUserMessage } from '@deepseek-ai/dsh-llm'

const subject = { tenantId: 'tenant-a', actorId: 'alice' }
const taskId = randomUUID(), sessionId = randomUUID()
ctx.enterprisePlatform.ledger.createTask({
  ...subject, taskId, sessionId, policyRevision: 1,
  provider: approvedProvider, model: approvedModel,
  maxAttempts: 4, maxTokens: 1024, expiresAt: Date.now() + 60_000,
  ticketId: 'T-42', expectedVersion: 1, canClose: false,
})
const handle = await createEnterpriseAgent(ctx, subject, taskId, sessionId)
try {
  handle.agent.followup(createUserMessage({
    content: [{ type: 'text', text: '读取工单 T-42，注明状态与版本。' }],
    source: { kind: 'user' }, // Only verified direct user input uses this source.
  }))
  await handle.agent.whenIdle()
  // Inspect turn/end and independently validate the business deliverable.
} finally {
  await handle.dispose()
}
```

`approvedProvider`／`approvedModel` 必须来自控制面已批准且宿主实际注册的路由。异步机器人／任务生产者不能假冒直接人类输入的 source；本段使用的是用户经可信入口提交的场景。本例没有任务报告验收器，也没有 DSH 持久 Session provider，whenIdle 不代表业务成功或日志耐久。

## 正式 profile 的接线骨架

安装本包后，可以用下述 insert patch 挂平台服务。企业 ingress 插件另行实现认证、任务路由和上面的调用；policy／ticket tool 在 setup 内按 Agent 挂载，不放在 root 全局挂载。**这个骨架完成配置准备，本轮没有运行完整 profile 或打包安装。**

```yaml
- insert:
    - id: enterprise-platform
      name: research-enterprise-harness
      config:
        databasePath: /srv/company-agent/enterprise.db
```

企业数据目录须预先建立并受部署系统保护。生产继续通过 `dsh --profile <受支持命名 profile> --patch <patch文件>` 启动；入口、模型 adapter 和其他依赖要在同一 profile 内就绪。本例不提供自建 Context 的生产启动程序，也不建议直接在标准 SDK 上假设存在本例的主体绑定。

平台服务不会自动给标准 SDK／Controller 创建的会话绑定主体和 policy。企业 ingress 必须统一执行可信 create／resume，其他入口按部署政策关闭或限制访问；同一个 session id 也不能恢复过期授权。不要把只插入平台服务的 patch 视为已经完成身份接入。

## 边界与清理

- 当前是 Node 24 上的本地 SQLite 参考 provider；`node:sqlite` 的可用性／发布状态应在目标 Node 版本核对。不是集群预算系统或生产权限平台。
- 额度计的是 Loop 的调用准入预留；解析失败也消耗一次，不计金额，不拦截直接摘要 LLM 调用。完整预算应覆盖受控 LLM 调用边界。
- 两连接和文件重开已经测试；未验证多进程抢占、分布式数据库或灾难恢复。
- Audit 表只存必要元数据，没有防篡改保证。最终工具 observer 不能成为业务写入的强审计屏障。
- 只支持本例 native tool policy；增加 PTC、子 Agent、workflow 时必须重新定义运输层和子主体政策。
- 策略的 mask／guard 随 Fiber 撤销；企业应用不应在活跃 Agent 上单独卸载安全政策。
- 测试最终释放 Handle／root Fiber，关闭数据库，删除临时目录；没有更改上游 tracked 源码。生产释放应先停止准入、排空 Handle，再关闭 provider。

SSO、真实模型、远端连接器、Vault、完整 profile 启动、packed install、UI、持久 Session 联调、跨平台与容量测试均未完成；请按[分阶段实施方案](../../04-enterprise-harness-practices.md#10-分阶段落地与技术判断)推进这些独立验证。
