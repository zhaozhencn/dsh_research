# DeepSeek Harness 固定版本源码研究

本目录围绕 DeepSeek Harness 的 16 项公共关注点，提供四篇主题文档、16 篇独立技术文章、源码证据、验证记录和扩展示例。内容覆盖架构组成、运行与恢复、插件开发，以及面向企业专属 Agent Harness 的工程实践。

研究由单一执行者完成。正文区分源码事实、官方说明、运行验证、分析推断和改造建议；企业方案与示例不能直接解释为上游已经提供的生产能力。

## 研究基线与范围

|项目|固定基线|
|---|---|
|研究日期|2026-10-04|
|Harness 包版本|`0.2.1-alpha.1`|
|上游提交|`5badb15009ae1756c3afe0ae0cef1faafc290ccc`|
|目录盘点|341 个 workspace 成员、14,208 个 tracked 文件|
|本机验证环境|Node 24.19.0、pnpm 11.7.0、TypeScript 6.0.3；macOS arm64|

后续的架构补充、技术专栏与企业实践均沿用这一提交，没有切换上游版本，也不将其称为持续更新的最新版本。完整目录盘点不意味着逐行阅读全部源码；核心机制深读、外围包清单核查与实际测试范围分别记录在[基线](appendices/baseline.md)和[覆盖清单](appendices/coverage.md)。

## 阅读导航

|文档／材料|内容与阅读用途|
|---|---|
|[01：宏观架构与系统设计](01-architecture.md)|建立系统地图，按 16 项关注点理解组成、职责与能力边界|
|[02：源码实现与运行流程](02-runtime-source.md)|追踪输入接纳、模型请求、工具执行、状态提交、失败恢复和资源清理|
|[03：二次开发与扩展实践](03-extension-practices.md)|查阅扩展接缝、替换矩阵、私有工作台方案和通用开发验收|
|[04：企业专属 Harness 开发实践](04-enterprise-harness-practices.md)|将 16 项关注点转成企业要求，展开身份授权、持久预算、业务幂等、审计和部署|
|[16 篇技术专栏](articles/README.md)|每项关注点独立成文，包含架构、代码、异常路径、优势与不足及技术心得|
|[扩展示例目录](examples/README.md)|最小工具、模型路由策略与企业工单参考实现的源码及复现入口|
|[源码证据索引](appendices/evidence-index.md)|149 条固定 SHA 源码／文档锚点，以及历史提交差异与运行证据|
|[验证记录](appendices/validation.md)|测试计数、精确命令、失败修复过程、文稿检查及验证限制|
|[待验证问题](appendices/open-questions.md)|既有研究的开放问题和上线前需要补足的验证|

建议按目的选择阅读路径：

- **理解框架**：01 → 02，再按需阅读对应技术专栏。
- **编写扩展**：03 → 最小示例，核对真实接口、作用域和清理契约。
- **建设企业 Harness**：04 → 企业工单示例，再回查 01／02 的相关机制。
- **复核研究或同步版本**：基线 → 覆盖 → 证据 → 验证记录，再使用仓库内的[研究同步技能](../../skills/harness-research-sync/SKILL.md)。

## 主要架构判断

1. **插件组合是核心扩展方式。** 具体 Loop 也是插件；Cordis Context 仍有框架基础。Scope／realm 管理逻辑可见性，不能代替租户或操作系统隔离。
2. **运行状态具有不同提交边界。** Session 事实、模型 surface、projection 和实时流各有职责；内存 append、`whenIdle` 与持久 flush 不能互相替代。
3. **工具执行与结果提交分阶段进行。** prepare 有序，允许并行的 body 有限并发，结果按模型顺序提交；超时和卸载需要底层工作响应取消并真正静止。
4. **恢复保留不确定性。** resume／fork 重建与修补历史，不会自动重跑已执行工具。未知结果应先核对业务事实，外部副作用没有统一回滚保证。
5. **企业治理需要额外控制面。** 业务验收、累计费用、授权撤销、持久产物及跨主机调度，应有独立状态与责任主体；目标完成自报、回合额度和遥测接缝不能替代这些能力。
6. **在线变更不等于业务事务。** 配置刷新与模块 HMR 的边界不同；撤销监听器不会抹去已有 Session 路由或外部写入，局部激活失败也不保证全局回滚。

这些判断及其条件、源码依据和改造建议分别展开在四篇主题文档中，不构成全平台或生产部署认证。

## 示例与技术专栏

|示例|实现重点|实际验证|
|---|---|---|
|[sum-tool](examples/sum-tool/README.md)|类型化工具参数、规范数值输出、取消与注册清理|真实 Loop 的工具结果回流、参数错误和卸载|
|[route-policy](examples/route-policy/README.md)|`agent/request` 路由、Agent scope 与持久 header|路由变化、作用域、卸载后旧会话／新实例差异和取消|
|[enterprise-harness](examples/enterprise-harness/README.md)|可信身份绑定、独立策略／工具插件、SQLite 调用预算、截止取消和幂等回执|16 个真实 Loop／本地账本用例，包括授权撤销、重试额度和事务故障注入|

原有两个最小插件共用 5 个测试用例，企业参考实现另有 16 个用例；均经过严格类型检查和 ESM 编译，测试加载编译后的插件并共享固定 checkout 的真实运行包。模型流由受控 adapter 提供，不涉及真实供应商网络。

企业示例只支持说明中约定的 native tool policy。平台服务的 profile patch 是接线骨架，不会自动改造标准 SDK／Controller 的身份和 Agent 创建路径；SSO、可信企业入口与真实业务连接器仍需实现。其 SQLite 账本是应用业务状态，不是 DSH SessionPersistence 的替代。

技术专栏配套 **33 段代码摘录、16 张 PNG 机制图及对应 SVG**，见[专栏目录](articles/README.md)。摘录来自固定提交或既有已验证研究代码；专栏写作与图片检查没有增加行为测试计数，也没有在微信公众号执行发布或预览。

## 验证结果与复现

当前去重计数为 **37 个测试文件、1,520 passed、1 conditional skipped**：

|范围|文件数|通过用例|条件跳过|
|---|---:|---:|---:|
|上游选定契约测试|35|1,499|1|
|两个最小扩展的自定义测试|1|5|0|
|企业参考实现的自定义测试|1|16|0|
|合计|37|1,520|1|

这不是全仓测试或覆盖率结果。计数按最终通过的独立用例去重，不累计失败重跑；原生 flock 缺失导致的初次失败、环境修复，以及企业示例 schema DSL 编写错误和修复均保留记录。详见[验证附录](appendices/validation.md)与[企业运行台账](validation/enterprise-runs.json)。

从仓库根目录复现企业示例，前提是固定 checkout、依赖及 vendor 声明已按[准备说明](examples/README.md)就绪：

```sh
node research/deepseek-harness/validation/enterprise-example.mjs typecheck
node research/deepseek-harness/validation/enterprise-example.mjs build
node research/deepseek-harness/validation/enterprise-example.mjs test
```

文稿检查与运行验证分开：当前材料包含原报告的 14 张 Mermaid 和企业实践的 2 张，均通过实际 parser 校验；PNG／SVG 另行检查。链接、SHA、区间和格式检查只证明材料可定位与结构一致，不自动证明技术结论。结果见[完整材料检查](validation/artifact-check.json)、[企业材料检查](validation/enterprise-check.json)和[专栏检查](validation/column-check.json)。

## 验证边界与维护约定

本研究没有验证真实模型服务、SSO／实际企业权限系统、远端业务幂等、Vault、完整 profile 启动／发布包安装、Web／Electron E2E、Python wheel、Linux／Windows 执行沙箱、持久 Session 与企业插件联调、集群调度或生产性能。

企业例的两连接／数据库重开属于同机 SQLite 验证；调用额度计的是 Loop attempt 的准入预留，不是金额预算，也没有覆盖直接摘要 LLM 调用。业务事务故障注入证明本地变更、回执与审计共同回滚，不能外推为远程 exactly-once。

源码 checkout 和本地环境放在仓库忽略的 `.sources/`，不复制进研究成果。更新文档和示例时应固定源版本，保留证据与失败记录，并如实说明新增、重跑及未验证范围；贡献流程见仓库根目录的[AGENTS.md](../../AGENTS.md)。
