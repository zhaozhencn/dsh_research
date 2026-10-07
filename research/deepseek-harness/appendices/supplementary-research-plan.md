# DSH 二次开发补充研究路线图

这份路线图将补充项组织成“研究模块 → 专题问题 → 源码主线 → 开发样例 → 验收证据”。目标是回答具体开发问题，并形成可复用的扩展契约和实例。

基线为 **`0.2.1-alpha.1`／`5badb15009ae1756c3afe0ae0cef1faafc290ccc`**。分类是面向二次开发的研究框架，不代表 DSH 源码原生存在六层架构。R01—R12 是研究标识，对应17—28篇正文；现有00—16篇及其映射保持原状。

当前状态为 **articles-generated**：12篇正文与48组图示已完成；源码、已有样例及选定契约测试已复核。真实企业部署和全部产品验收不在本批结论内，详见[验证记录](../validation/supplementary-articles-validation.md)。机器可读版本见[专题计划 JSON](../validation/supplementary-research-plan.json)。

拟定文档列表、17—28篇的逐篇章节以及配套文档大纲见[文档列表与写作大纲](supplementary-article-outlines.md)。篇次是写作安排，R01—R12 继续作为研究计划标识使用。

## 1. 从公共关注点进入具体开发问题

现有专栏已经解释执行、状态、安全、治理与生命周期。补充研究沿这些事实追踪具体子系统，重点解释挂载位置、跨对象交接、提交点和失败处理。已有段落是前置阅读材料；新专题通过完整源码主线、独立样例和验证记录深化。

## 2. 六个研究模块

|模块|核心问题|专题|开发成果方向|
|---|---|---|---|
|M01 对象与能力组织|一个 Agent 怎样获得自己的运行环境|R01、R02|正确装配的 Agent 与企业 SOP|
|M02 配置与扩展管理|运行中的配置与插件怎样被管理|R03、R04|可管理的配置与扩展包|
|M03 前后端与系统接入|业务系统和用户界面怎样接入 Harness|R05、R06|可接入的业务服务与界面|
|M04 外部能力与程序执行|外部工具与模型程序怎样进入受控执行链|R07、R08|可调用的远端能力与程序运行|
|M05 任务编排与企业集成|多个执行单元怎样形成有业务结果的任务|R09、R10|有结果契约的业务任务|
|M06 身份治理与产品交付|运行边界怎样落到企业身份和可安装产品|R11、R12|有明确身份边界的发行产品|

身份治理是跨模块责任。M06 的分类位置不表示授权可以最后补做；企业身份和资源边界应在真实业务接入前明确。

## 3. 专题总表与前置关系

P0 表示先补核心开发链路，P1 表示后续深化；“条件前置”表示一旦进入企业相关场景应提前落实设计。依赖是研究和样例组织顺序，不是运行时调用图；各专题仍需阅读现有基础文章。

|标识|专题|优先级|前置专题|研究性质|
|---|---|---|---|---|
|R01|[Agent 的创建、作用域与 preset 装配](#r01)|P0|现有基础文章|既有源码深化|
|R02|[Skill 与工作区指令的发现、选择和加载](#r02)|P0|R01|既有源码深化|
|R03|[设置表单、配置写回与运行生效](#r03)|P0|现有基础文章|既有源码深化|
|R04|[Plugin Manager 与扩展包管理生命周期](#r04)|P1|R03|既有源码深化|
|R05|[一个完整前后端插件的装配与调用](#r05)|P0|R01、R03|既有源码深化|
|R06|[SDK、ACP 与 Web 的接入边界](#r06)|P0|R01|既有源码深化|
|R07|[MCP 连接、发现、重连与能力撤销](#r07)|P0|R01|既有源码深化|
|R08|[PTC 的程序执行与内部工具调用](#r08)|P1|R01|既有源码深化|
|R09|[Workflow、Schedule 与 Hooks 的编排边界](#r09)|P1|R01、R08|既有源码深化|
|R10|[企业数据与远端执行的接入设计](#r10)|条件前置|R01、R07、R11|源码深化＋企业新增设计|
|R11|[身份、凭据与企业租户边界](#r11)|条件前置|R01、R06|源码深化＋企业新增设计|
|R12|[构建、打包、安装与发行验证](#r12)|P1|R04、R05、R06|既有源码深化|

## 4. 各专题的研究边界与交付要求

<a id="r01"></a>

### R01 Agent 的创建、作用域与 preset 装配

**中心问题：** Host 启动之后，一个完整且可执行的 Agent 如何建立？

**需要回答：**

1. Agent、Session、Context、Scope 分别保存什么身份和状态，谁拥有和释放？
2. create/setup/commit/publication 怎样交接，创建失败如何撤销未发布资源？
3. preset revision 怎样保留，子 Agent 怎样继承，resume/fork 怎样再次装配？

**源码入口：** [packages/core/agent/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent/src/index.ts)；[packages/core/scope/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/scope/src/index.ts)；[packages/preset/agent-preset-registry/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/preset/agent-preset-registry/src/index.ts)。

**现有衔接：** [00](../articles/00-config-loading-startup.md)、[01](../articles/01-plugin-lifecycle.md)、[03](../articles/03-agent-loop.md)、[06](../articles/06-state-persistence.md)、[09](../articles/09-concurrency.md)。

**预期产出：** 带 scoped 工具和策略的 Agent 创建示例，附对象所有权图。

**验收要求：** 成功创建后能力可用；setup 失败不发布 Agent；退出释放资源。

**范围边界：** Scope 和 Context 的能力可见性不能直接作为不可信代码或租户隔离证明。

<a id="r02"></a>

### R02 Skill 与工作区指令的发现、选择和加载

**中心问题：** 一份企业指令如何成为当前 Agent 可以发现和消费的能力？

**需要回答：**

1. provider、候选、catalog 和完整正文分别怎样生产与消费？
2. 同名来源、作用域、invocation policy、缓存及失效怎样影响选择？
3. Skill、AGENTS.md 和文件引用通过哪些不同路径进入 Session，何时更新和清理？

**源码入口：** [packages/skill/skill/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/skill/skill/src/index.ts)；[packages/skill/skill-filesystem/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/skill/skill-filesystem/src/index.ts)；[packages/skill/tool-skill/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/skill/tool-skill/src/index.ts)；[packages/context/agent-instructions/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/context/agent-instructions/src/index.ts)。

**现有衔接：** [01](../articles/01-plugin-lifecycle.md)、[05](../articles/05-context-engineering.md)、[10](../articles/10-security.md)。

**预期产出：** 企业 SOP Skill 的 provider 与加载示例，附来源选择和指令进入 Session 的流程。

**验收要求：** 核对同名选择、catalog/正文分离、来源变更及取消；说明结果作用域。

**范围边界：** 指令加载和工具执行授权分别研究；invocation policy 不等于企业认证。

<a id="r03"></a>

### R03 设置表单、配置写回与运行生效

**中心问题：** 用户修改一个设置后，磁盘配置和运行实例分别发生了什么？

**需要回答：**

1. Config schema、volatile 字段、表单描述与 live 值怎样对应？
2. revision、secret 保留、update/replace/mutate/reset 怎样参与写入？
3. config-editor 怎样生成 patch，更新怎样到达 Entry/Fiber，失败留下什么状态？

**源码入口：** [packages/settings/settings/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/settings/settings/src/index.ts)；[packages/boot/config-editor/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/boot/config-editor/src/index.ts)；[packages/api/settings-controller/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/settings-controller/src/index.ts)。

**现有衔接：** [00](../articles/00-config-loading-startup.md)、[01](../articles/01-plugin-lifecycle.md)、[02](../articles/02-deployment-evolution.md)。

**预期产出：** 可配置业务插件的设置与写回示例，附字段值、raw config、patch 和实例的交接图。

**验收要求：** 验证正常保存、陈旧 revision、secret 保留及失败边界；区分保存与运行生效。

**范围边界：** Settings 字段编辑与 patch 整个 config 覆盖各有契约，不混为同一种 merge。

<a id="r04"></a>

### R04 Plugin Manager 与扩展包管理生命周期

**中心问题：** 一个扩展包从安装到启用、移除，经过哪些提交和清理边界？

**需要回答：**

1. 包操作、profile 锁、manifest 与 lockfile 怎样协调？
2. bundle 选择、兼容检查、RuntimeResolution 发布和 HMR 怎样衔接？
3. 安装取消、验证失败、启用失败和移除失败分别保留或恢复哪些事实？

**源码入口：** [packages/boot/plugin-manager/src/operations.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/boot/plugin-manager/src/operations.ts)；[packages/boot/plugin-manager/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/boot/plugin-manager/src/index.ts)；[packages/boot/app-boot/src/profile.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/boot/app-boot/src/profile.ts)。

**现有衔接：** [00](../articles/00-config-loading-startup.md)、[01](../articles/01-plugin-lifecycle.md)、[02](../articles/02-deployment-evolution.md)、[10](../articles/10-security.md)。

**预期产出：** 教学 bundle 的安装/启停/移除案例，附阶段结果和恢复矩阵。

**验收要求：** 分别验证保存状态、安装状态、激活状态；失败和取消后清理包管理进程。

**范围边界：** 管理操作涉及 Host 代码和安装脚本；配置恢复不等于包目录及业务副作用的全局回滚。

<a id="r05"></a>

### R05 一个完整前后端插件的装配与调用

**中心问题：** 一个业务功能如何从 Host 服务进入浏览器，并在卸载时完整退出？

**需要回答：**

1. dsh.client、Loader 扫描、Web boot graph 与 Client 激活怎样连接？
2. Remote 声明、Typert 生成、参数/返回值、Context lookup、流和取消怎样交接？
3. UI Slots、store、事件与 effect 怎样组织展示并处理重连和卸载？

**源码入口：** [packages/client/modules/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/client/modules/src/index.ts)；[packages/api/gateway/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/gateway/src/index.ts)；[packages/client/ui-slots/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/client/ui-slots/src/index.ts)；[docs/development.md](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/docs/development.md)。

**现有衔接：** [00](../articles/00-config-loading-startup.md)、[01](../articles/01-plugin-lifecycle.md)、[16](../articles/16-interaction-deliverables.md)。

**预期产出：** 业务服务＋Remote API＋Client 插件＋UI 面板的完整样例。

**验收要求：** 正常调用与展示；断线/取消后的正确状态；卸载后调用和展示资源撤销。

**范围边界：** 实例须完成类型生成和 Client 构建；源码可调用不等于浏览器产物可用。

<a id="r06"></a>

### R06 SDK、ACP 与 Web 的接入边界

**中心问题：** 企业应用应通过哪种入口创建 Session 并驱动同一运行内核？

**需要回答：**

1. 各入口怎样创建/恢复 Session、传递参数和业务输入？
2. 结果、审批、事件、错误与取消分别经过哪些协议对象？
3. SDK 子进程、连接与 Session 由谁拥有，调用方关闭后怎样处理？

**源码入口：** [packages/sdk/client/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/sdk/client/src/index.ts)；[packages/sdk/server/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/sdk/server/src/index.ts)；[packages/acp/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/acp/README.md)；[packages/api/session-controller/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/session-controller/src/index.ts)。

**现有衔接：** [00](../articles/00-config-loading-startup.md)、[03](../articles/03-agent-loop.md)、[06](../articles/06-state-persistence.md)、[11](../articles/11-autonomy.md)、[16](../articles/16-interaction-deliverables.md)。

**预期产出：** 同一教学任务的入口对比及一个可运行 SDK 集成示例。

**验收要求：** 核对接纳与完成、正常结果、审批/取消和调用方退出；记录子进程清理。

**范围边界：** 协议能力逐项核对，不假定 SDK、ACP 与 Web 的所有操作完全等价。

<a id="r07"></a>

### R07 MCP 连接、发现、重连与能力撤销

**中心问题：** 远端能力如何变成本地可见、可调用且有生命周期的工具与资源？

**需要回答：**

1. stdio/HTTP 连接与初始 readiness 怎样建立？
2. 工具发现、命名、schema、resources 和 instructions 怎样接入各自消费者？
3. 重连 generation、注册更换、执行取消与 dispose 怎样衔接？

**源码入口：** [packages/mcp/mcp-client/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/mcp/mcp-client/src/index.ts)；[packages/mcp/mcp-client/src/connection.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/mcp/mcp-client/src/connection.ts)；[packages/mcp/mcp-client/src/tools.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/mcp/mcp-client/src/tools.ts)；[packages/mcp/mcp-resources/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/mcp/mcp-resources/src/index.ts)。

**现有衔接：** [07](../articles/07-tool-runtime.md)、[08](../articles/08-reliability.md)、[10](../articles/10-security.md)。

**预期产出：** 受控 MCP server 的连接与调用样例，附连接代际和注册生命周期。

**验收要求：** 验证正常调用、断线/重新发现、取消与卸载；明确远端副作用是否可确认。

**范围边界：** MCP connection、instructions 和工具注册不替代资源授权或远端幂等协议。

<a id="r08"></a>

### R08 PTC 的程序执行与内部工具调用

**中心问题：** 模型程序如何通过 bindings 调用工具，并返回可解释的结果？

**需要回答：**

1. native/ptc/both presentation、生成 SDK/bindings 与 run_code 怎样形成请求？
2. 运行进程、内部工具派发、权限、超时和并发怎样交接？
3. 程序结果、工具结果、输出、取消与进程清理分别由谁提交？

**源码入口：** [packages/core/agent-tool-presentation/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-tool-presentation/src/index.ts)；[packages/ptc-runtime/ptc-runtime/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/ptc-runtime/ptc-runtime/src/index.ts)；[packages/ptc-runtime/ptc-runtime-node/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/ptc-runtime/ptc-runtime-node/src/index.ts)。

**现有衔接：** [07](../articles/07-tool-runtime.md)、[08](../articles/08-reliability.md)、[09](../articles/09-concurrency.md)、[10](../articles/10-security.md)、[12](../articles/12-budgets.md)。

**预期产出：** 调用两个受控工具的程序示例，附内部调用链、失败和取消记录。

**验收要求：** 验证内部工具授权；程序/工具错误可区分；取消后清理进程。

**范围边界：** PTC runtime 与 Session/工具语义分别核对，不预设性能提升幅度。

<a id="r09"></a>

### R09 Workflow、Schedule 与 Hooks 的编排边界

**中心问题：** 任务编排、定时触发和执行钩子各自负责哪一段运行过程？

**需要回答：**

1. 分别建立三种机制的入口、执行者与结果链，不拼成虚构的统一调用链。
2. 父子任务、触发来源、取消、重入与清理怎样表达？
3. 逐项核对持久性、重启行为、失败传播和重复触发范围。

**源码入口：** [packages/workflow/workflow/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/workflow/workflow/src/index.ts)；[packages/workflow/workflow-ptc/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/workflow/workflow-ptc/src/index.ts)；[packages/schedule/schedule/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/schedule/schedule/src/index.ts)；[packages/hooks/hook-protocol/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/hooks/hook-protocol/src/index.ts)。

**现有衔接：** [08](../articles/08-reliability.md)、[09](../articles/09-concurrency.md)、[11](../articles/11-autonomy.md)、[15](../articles/15-task-completion.md)。

**预期产出：** 任务编排示例与三种机制的寿命/恢复对照表。

**验收要求：** 核对普通失败、基础设施失败、取消、重复触发与 owner 退出；说明实际持久范围。

**范围边界：** 不预设 Schedule 是持久企业调度器，或 Workflow 有业务事务保证。

<a id="r10"></a>

### R10 企业数据与远端执行的接入设计

**中心问题：** 业务数据、知识检索和远端执行怎样通过扩展接缝进入任务？

**需要回答：**

1. 沿 fs/shell/subprocess/workspace provider 找到定义、调用方和替换边界。
2. 用具体系统说明数据返回前授权、凭据使用、检索来源和远端操作回执。
3. 连接丢失、取消、未知结果、再次执行与产物保存怎样取得可验证事实？

**源码入口：** [packages/fs/fs/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/fs/fs/src/index.ts)；[packages/shell/shell/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/shell/shell/src/index.ts)；[packages/subprocess/subprocess/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/subprocess/subprocess/src/index.ts)；[packages/workspace/workspace/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/workspace/workspace/src/index.ts)。

**现有衔接：** [07](../articles/07-tool-runtime.md)、[08](../articles/08-reliability.md)、[10](../articles/10-security.md)、[15](../articles/15-task-completion.md)、[16](../articles/16-interaction-deliverables.md)。

同时承接[企业二次开发报告](../04-enterprise-harness-practices.md)，先核实已有契约，再标明企业新增部分。

**预期产出：** 企业数据查询＋一次可确认业务写入的案例；需要远端执行时单列 provider 协议。

**验收要求：** 受控外部系统验证权限、幂等/未知结果、取消与交付；显式记录 mock 范围。

**范围边界：** provider 契约是源码研究；企业 connector、RAG 或远端后端是新增设计，不描述为默认能力。

<a id="r11"></a>

### R11 身份、凭据与企业租户边界

**中心问题：** 可信主体如何关联 Agent、Session、Workspace、模型、凭据和业务资源？

**需要回答：**

1. 盘点请求可信性、Context lookup、Session/Workspace 归属与凭据保护的既有边界。
2. 定义 principal/tenant 与授权策略的新契约，定位跨租户与后台任务检查。
3. 恢复、delegation、缓存、审计和撤权后再次执行时，哪些身份必须重新验证？

**源码入口：** [packages/client/connection/src/api-request-trust.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/client/connection/src/api-request-trust.ts)；[packages/api/gateway/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/gateway/src/index.ts)；[packages/credentials/credentials/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/credentials/credentials/src/index.ts)；[packages/credentials/credentials-local/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/credentials/credentials-local/src/index.ts)。

**现有衔接：** [06](../articles/06-state-persistence.md)、[09](../articles/09-concurrency.md)、[10](../articles/10-security.md)、[13](../articles/13-observability.md)。

同时承接[企业二次开发报告](../04-enterprise-harness-practices.md)，先核实已有契约，再标明企业新增部分。

**预期产出：** 企业授权链设计、资源归属矩阵及越权/撤权测试案例。

**验收要求：** 验证跨租户拒绝、凭据不越界、恢复与子任务重新授权；区分进程与资源隔离。

**范围边界：** 承接企业报告已有责任划分继续深化，不宣称 DSH 当前已有完整多租户平台。

<a id="r12"></a>

### R12 构建、打包、安装与发行验证

**中心问题：** 二次开发成果怎样从源码成为目标环境真正可运行的产品？

**需要回答：**

1. 追踪 Host/Client build faces、Typert 产物、exports 与 native 依赖。
2. 核对 Web/Desktop/SDK 产物怎样提供 profiles、bundles 和运行入口。
3. 建立实际安装、旧数据、退出排空、升级失败及依赖兼容验证矩阵。

**源码入口：** [docs/development.md](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/docs/development.md)；[package.json](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/package.json)；[scripts/build.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/scripts/build.ts)；[apps/desktop/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/apps/desktop/README.md)。

**现有衔接：** [00](../articles/00-config-loading-startup.md)、[02](../articles/02-deployment-evolution.md)、[14](../articles/14-evaluation.md)。

**预期产出：** 教学扩展的打包与安装记录，附产物依赖图和目标环境矩阵。

**验收要求：** 从产物启动；记录目标平台、依赖、退出与升级的实际验证限制。

**范围边界：** 完整发行研究最后汇总；每个样例所需构建和类型生成从一开始执行。

## 5. 研究顺序与阶段成果

|阶段|研究安排|完成后应具备什么|
|---|---|---|
|S1 对象与能力基础|R01 → R02；R03 可并列研究|能说明 scoped 能力挂载位置，以及设置写回与生效。|
|S2 完整开发链|R05、R06、R07；R04 接续配置管理|能接入业务服务、界面、SDK 或 MCP，并管理扩展。|
|S3 程序执行与编排|R08 → R09|能追踪程序与子任务的执行、取消、提交及清理。|
|S4 企业集成与验收|满足 R11 身份设计前置后开展 R10；R12 汇总发行验证|能提供业务效果、授权边界和安装产物的实际证据。|

并列表示研究可独立安排，不要求委派或多个 Agent 执行。R11 可在 R01、R06 契约明确后提前开展。R12 的构建知识随样例使用随查证，最后汇总发行与目标环境验证。

## 6. 统一研究记录，正文服从各自机制

|记录单元|必须保存的信息|
|---|---|
|整体机制|业务场景、入口、中心问题、对象关系与边界。|
|调用和数据|caller、callee、输入输出、关键结构、消费位置、await 与提交点。|
|生命周期|装配、激活、运行、更新、取消、恢复、清理；不适用环节明确说明。|
|源码证据|固定 SHA、真实符号、局部原文与行号；区分事实、官方说明和推断。|
|开发实践|最小可运行样例、修改位置、配置、构建与启动方式。|
|验证证据|正常和代表性异常路径、命令、退出码、日志、实际范围与限制。|
|工程认识|从正文具体选择推导适用条件和改造方法。|

图示服务整体机制、关键交接、核心数据和异常边界，分布在相应正文附近；长篇可沿用四图组织，具体图型服从机制。函数切换说明真实关系，专业名词保留英文。详细方法沿用[文章深化方法](article-refinement-methodology.md)和项目级技能。

## 7. 三份跨专题维护的研究资产

|资产|核心字段|服务的开发决策|
|---|---|---|
|扩展契约矩阵|定义/provider/consumer、注册位置、Context/Scope、提交点、释放责任、验证入口。|新能力挂载位置与兼容责任。|
|完整扩展样例|业务工具、Host 服务、Remote API、Client UI、设置表单和 bundle；按阶段增量完成。|多个契约如何协同形成可运行功能。|
|改动影响与回归矩阵|改动点、调用者/协议/数据影响、需重建产物、测试和目标环境。|修改或升级后的复核范围。|

三份资产是后续专题持续积累的交付物。本轮只定义范围，不标为已实现或验证。

## 8. 完成判定与当前限制

专题完成需要明确中心问题、可追溯源码主线、准确对象与边界说明，以及与范围相称的样例和验证记录。验证受凭据或平台限制时，完成可行部分并记录限制；mock、接口存在或构建通过不能直接写成生产验收。

源码深化不新增能力承诺；企业设计分别列出可复用契约与新增实现。后续同步版本时重新固定 SHA 并复核依赖、调用与数据语义，本计划入口不自动成为新版本结论。

本轮已完成17—28正文、配图和三个配套说明；现有00—16正文及插图保持原状。计划中的生产部署、真实身份/外部系统与完整发行验收仍按实际验证边界分别管理；没有发布产品。

[专栏目录](../articles/README.md) · [企业二次开发报告](../04-enterprise-harness-practices.md) · [机器可读计划](../validation/supplementary-research-plan.json)
