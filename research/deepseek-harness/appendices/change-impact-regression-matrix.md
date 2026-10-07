# DSH 改动影响与回归矩阵

本矩阵基于17—28篇源码分析，帮助企业扩展和后续上游同步选择检查范围。当前源码固定为 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`；表中“应复核”是升级时的任务，并不表示本批已经完成生产验收。

## 1. 由变化定位消费者

|变化面|可能影响|应复核的主要契约|代表测试/验证入口|
|---|---|---|---|
|Agent factory/setup/Scope|创建观察者、preset、入口及授权绑定|发布顺序、setup/listener 失败、late handle 与 owner exit|`core/agent-loop/tests/scope-lifecycle.spec.ts`|
|preset generation|子 Agent、Skill/tools 可见性|精确 revision 继承、rebind、users 与 retired 回收|`preset/agent-preset-registry/tests/registry.spec.ts`|
|Skill discovery/cache|catalog、user/model loader|Scope 同名、complete、revision、正文变化与撤销|`skill/skill/tests/skill.spec.ts`、`tool-skill.spec.ts`|
|Config/schema/volatile|表单、patch、live consumer|revision 冲突、secret 保留、继承 reset、激活补偿|`settings/settings/tests/configuration*.spec.ts`|
|Plugin Manager/pnpm|profile 依赖、选择、HMR、安装脚本|锁、取消阶段、进程树、repair、restart-required|`boot/plugin-manager/tests/manager.spec.ts`、`operations.spec.ts`|
|Remote descriptor/Gateway|typed Client、Context lookup、streams|严格定义撤销、参数还原、错误、取消与 carrier generation|`api/gateway/tests/gateway.host.spec.ts`|
|Client graph/Slots/store|browser boot、卡片与卸载|exports、模块冲突、namespace 可用性、staged state/late result|`client/modules/tests/node-half.client.spec.ts`；设置卡片测试|
|SDK/ACP|子进程、Session、业务调用方|initialize、接纳身份、idle 结算、timeout abandonment、退出|`sdk/client/tests/{sdk-client,launch,dispose}.spec.ts`|
|MCP|工具集合、resources、instructions|fetch/swap 差异、重连预算、late generation、dispose|`mcp/mcp-client/tests/{reconnect,negotiation-lifecycle}.spec.ts`|
|PTC/ToolRuntime|program ABI、权限、并发、日志|bindings 校验、实际 subcall guard、budget/abort/cleanup|`ptc-runtime/ptc-runtime-node/tests/{bindings,runtime}.spec.ts`|
|Workflow/Schedule/Hooks|children、durable reminders、policy|parse/result、late child、flush/task commit、dialect mapping|`workflow-ptc/tests/integration.spec.ts`；schedule recovery；hook bridge|
|SSH/provider seam|远端 paths、helper、streams/进程|digest、版本、private identity、断线 unknown、清理等待|`ssh/fs-ssh/tests/provider.spec.ts`、`protocol-disposal.spec.ts`|
|Credentials/enterprise identity|轮换、Subject、资源隔离|来源优先级、锁内写、stale Agent、revoke、await 后检查|`credentials-local/tests/local.spec.ts`；企业16项集成测试|
|Build/package/native|types、Client、安装与升级|Host→Typert→Client、exports/files、digest、目标平台|build environment tests、pack smoke、真实产物启动|

测试路径均相对上游 `packages/`，`scripts/` 入口另注明。本地企业验证从研究仓库根运行，具体命令见[本批记录](../validation/supplementary-articles-validation.md)。

## 2. 新版本同步流程

先记录旧/新 full SHA 与 toolchain，按 changed files 定位上表的生产者及直接消费者；检查接口形状之外，也检查 await、提交点和 disposer 顺序。变化后的摘录重新从 Git object 提取，不沿用旧行号冒充新证据。

重新生成文章计划、例子及图定义，再运行最小有意义的回归。若实际接口改变导致 mock 也要改，保留旧失败和改动原因；如果源码测试通过但 tarball 缺文件，按发行问题处理，不扩大源码测试结论。

最后更新导航、source manifest、验证结果与未验收项。旧测试记录作为历史证据保留，不能简单覆盖成“最新全部通过”。版本同步可沿项目的 `harness-research-sync` 与 `source-code-article-refiner` 工作流执行。

## 3. 验证分层与放行范围

|证据层|可以支持|不能单独支持|
|---|---|---|
|固定源码/逐段 hash|实现可追溯、摘录准确|运行正确或生产可靠|
|mock/contract tests|所测边界和退出路径|真实模型、远端效果及企业身份|
|compiled integration|编译产物和真实内核在 fixture 内协作|完整安装或多节点部署|
|tarball ledger consumer|打包清单、ledger 独立导入与 receipt|其他插件 peers 或整个 Harness 安装|
|真实平台/业务验收|对应平台及受控资源的任务效果|未覆盖平台与无条件版本兼容|

本批实测与未验收项严格按这些层次记录。它们给后续升级提供复核起点，而不是一份自动允许发布的统一许可证。
