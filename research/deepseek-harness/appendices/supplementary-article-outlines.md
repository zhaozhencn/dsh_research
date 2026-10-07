# DSH 二次开发补充专栏：文档列表与写作大纲

本文件承接[补充研究路线图](supplementary-research-plan.md)，把六个研究模块、12个专题落实为拟定文档、章节大纲、核心数据、配图位置和开发验证任务，作为后续逐篇写作的直接依据。

研究基线为 **`0.2.1-alpha.1`／`5badb15009ae1756c3afe0ae0cef1faafc290ccc`**。现有00—16篇保持原状；新专题已续接17—28篇。R01—R12 是研究标识，17—28是文章篇次。本文保留原写作大纲；本批正文、四图与验证范围见[补充专栏目录](../articles/README.md#补充专栏17—28)及[验证记录](../validation/supplementary-articles-validation.md)。

## 1. 文档列表

文章计划保存在 `research/deepseek-harness/articles/`。下表列出已经生成的正文目标；标题继续定位本文件的详细大纲，正文入口见补充专栏目录。

|模块|研究标识／拟定篇次|拟定标题|拟定文件名|优先级|
|---|---|---|---|---|
|M01 对象与能力组织|R01／17|[从 Host 到一个可运行的 Agent：创建、Scope 与 preset 装配](#article-17)|`17-agent-creation-composition.md`|P0|
|M01 对象与能力组织|R02／18|[企业指令如何进入 Agent：Skill 发现、选择与按需加载](#article-18)|`18-skill-instruction-loading.md`|P0|
|M02 配置与扩展管理|R03／19|[一个设置怎样真正生效：表单、patch 写回与实例更新](#article-19)|`19-settings-config-writeback.md`|P0|
|M02 配置与扩展管理|R04／20|[扩展包如何进入运行系统：安装、启停、移除与恢复边界](#article-20)|`20-plugin-package-management.md`|P1|
|M03 前后端与系统接入|R05／21|[从后端服务到浏览器面板：一个完整 DSH 插件的实现链](#article-21)|`21-fullstack-plugin-development.md`|P0|
|M03 前后端与系统接入|R06／22|[让业务系统驱动 DSH：SDK、ACP 与 Web 的入口选择](#article-22)|`22-sdk-acp-web-integration.md`|P0|
|M04 外部能力与程序执行|R07／23|[一个 MCP server 怎样成为 Agent 能力：连接、发现与重连](#article-23)|`23-mcp-connection-lifecycle.md`|P0|
|M04 外部能力与程序执行|R08／24|[模型程序如何受控执行：PTC、bindings 与内部工具调用](#article-24)|`24-ptc-program-execution.md`|P1|
|M05 任务编排与企业集成|R09／25|[从 Agent 执行到任务编排：Workflow、Schedule 与 Hooks](#article-25)|`25-workflow-schedule-hooks.md`|P1|
|M05 任务编排与企业集成|R10／26|[把企业数据与远端操作接入 DSH：provider、授权与效果确认](#article-26)|`26-enterprise-data-remote-execution.md`|企业条件前置|
|M06 身份治理与产品交付|R11／27|[企业 Agent 的身份边界：可信入口、凭据与租户资源授权](#article-27)|`27-identity-credentials-tenancy.md`|企业条件前置|
|M06 身份治理与产品交付|R12／28|[从源码到企业发行包：构建、安装、升级与验证](#article-28)|`28-build-package-distribution.md`|P1|

优先级与篇次承担不同职责：篇次按模块排列，研究顺序按前置关系安排。企业接入时，第27篇身份设计应在第26篇真实资源接入前落实；各示例所需构建随开发执行，第28篇汇总发行验证。

## 2. 写作与证据约定

每篇开头说明业务场景、中心问题、入口、主线和对象关系。正文按真实调用、事件和数据交接展开，首次关键消费前解释相应结构。每次函数切换说明 caller、参数来源、callee、返回值或事件 consumer，关键步骤交代 await、提交点及失败处理。

下面的章节名称是写作提纲；涉及函数和数据的具体声明、字段、代码行号及异常行为，应在固定提交中逐项核实后进入正文。源码事实、官方说明、实测结果、推断及企业新增设计分别表述，不用预期验收项冒充测试结果。

沿用[项目文章深化方法](article-refinement-methodology.md)：保留 Agent、Session、Scope、Turn、Step、Fiber 等术语；源码摘录保持原文，连接上下文讲解。配图计划每篇四张，分布于整体介绍、关键交接、数据或寿命、异常边界，实际形态按源码核验结果确定。

示例可围绕“企业任务工作台”逐步复用业务工具、Host 服务、Client 面板、设置和 bundle。各篇仍可独立阅读；跨篇复用的代码应标明入口和依赖，不让读者靠其他文章补齐关键实现。

## 3. 逐篇详细大纲

<a id="article-17"></a>

### 17. 从 Host 到一个可运行的 Agent：创建、Scope 与 preset 装配

**定位：** M01 对象与能力组织 · R01 · 既有源码深化。

**目标文件：** `articles/17-agent-creation-composition.md`

**中心问题：** Host 启动之后，一个完整且可执行的 Agent 如何建立？

**前置阅读：** [00](../articles/00-config-loading-startup.md)、[01](../articles/01-plugin-lifecycle.md)、[03](../articles/03-agent-loop.md)、[06](../articles/06-state-persistence.md)、[09](../articles/09-concurrency.md)；前置专题：无新增专题依赖。

**重点数据与对象：** Agent / Session / Context / Scope 的身份与引用；创建输入与 setup/commit 边界；preset revision 与引用寿命。

**章节大纲：**

1. **整体地图：启动完成以后，还需要装配什么。** 从 Host 的公共服务进入 Agent 的 scoped 能力，说明创建、发布和开始执行各自的完成条件。
2. **对象与所有权：Agent、Session、Context 和 Scope。** 在首次创建前解释身份、状态、父子关系和释放责任，画出持久数据与运行实例的区别。
3. **创建入口：从调用参数进入 AgentRegistry.create()。** 追踪参数校验、Session 元数据及初始历史的准备，说明返回 handle 由谁消费。
4. **发布之前：setup、commit 与观察者通知。** 逐步说明能力注册、异步准备、提交和发布；沿失败路径核对未发布资源的清理。
5. **preset 装配：选择、revision 保留与子 Agent 继承。** 追踪能力组合绑定到当前 Agent 的过程，解释旧 revision 为什么仍可能被已有实例持有。
6. **resume、fork 和退出：复用哪些事实，重建哪些能力。** 分别核对恢复历史、重建 Context、父子归属与清理，不把恢复日志等同于恢复全部运行缓存。
7. **开发示例与验证：创建一个有业务工具和策略的 Agent。** 给出真实挂载、创建和调用步骤，并验证正常发布、setup 失败和 owner 退出。
8. **工程心得：能力完整性应在发布边界建立。** 从创建时的准备和提交提炼扩展方式，说明 scoped 能力可见性与进程隔离的不同责任。

**源码研究入口：**

- [packages/core/agent/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent/src/index.ts)
- [packages/core/scope/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/scope/src/index.ts)
- [packages/preset/agent-preset-registry/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/preset/agent-preset-registry/src/index.ts)

**四图安排：**

- 图1：Host/Agent/Session/Scope 所有权图，放在整体介绍之后。
- 图2：create→setup→commit→publication 时序图，放在首次关键数据或装配说明处。
- 图3：preset revision 保留与父子继承图，放在核心执行与数据交接处。
- 图4：创建失败、恢复与退出分支图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 带 scoped 工具和策略的 Agent 创建示例，附对象所有权图。 成功创建后能力可用；setup 失败不发布 Agent；退出释放资源。

**范围边界：** Scope 和 Context 的能力可见性不能直接作为不可信代码或租户隔离证明。

<a id="article-18"></a>

### 18. 企业指令如何进入 Agent：Skill 发现、选择与按需加载

**定位：** M01 对象与能力组织 · R02 · 既有源码深化。

**目标文件：** `articles/18-skill-instruction-loading.md`

**中心问题：** 一份企业指令如何成为当前 Agent 可以发现和消费的能力？

**前置阅读：** [01](../articles/01-plugin-lifecycle.md)、[05](../articles/05-context-engineering.md)、[10](../articles/10-security.md)；前置专题：R01。

**重点数据与对象：** provider 与候选/summary/definition；cwd、Scope 与 catalog 观察状态；invocation policy、来源和缓存失效。

**章节大纲：**

1. **整体地图：指令来源、发现目录与实际正文。** 先区分 Skill catalog、加载后的指令、工作区指令和文件引用，说明它们各自怎样服务任务。
2. **注册入口：provider 怎样贡献候选。** 解释 provider 的生产职责、候选与完整正文的数据差异，追踪注册与撤销。
3. **来源选择：目录、作用域与同名冲突。** 沿 filesystem discovery 和 registry 合并说明优先级、去重、调用方范围与异常来源处理。
4. **catalog：缓存、观察完整性与变更通知。** 追踪 catalog 的生成、缓存键和 revision，说明来源变化时哪些消费者应重新读取。
5. **按需加载：从名称选择到工具与 Session 消费。** 解释 model/user invocation policy、正文加载、取消和陈旧选择处理，回到实际调用方。
6. **独立指令路径：AGENTS.md 与文件引用。** 分别追踪工作区指令和引用进入历史及更新的过程，明确它们与 Skill 的衔接而非假设共用入口。
7. **开发示例与验证：一个企业 SOP Skill。** 实现最小 provider 或本地 Skill，验证同名选择、按需加载、来源变化和不可调用策略。
8. **工程心得：目录可见、正文加载和执行授权分别建立事实。** 从来源和消费边界解释 SOP 接入方式，明确指令内容不能自行产生工具权限。

**源码研究入口：**

- [packages/skill/skill/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/skill/skill/src/index.ts)
- [packages/skill/skill-filesystem/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/skill/skill-filesystem/src/index.ts)
- [packages/skill/tool-skill/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/skill/tool-skill/src/index.ts)
- [packages/context/agent-instructions/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/context/agent-instructions/src/index.ts)

**四图安排：**

- 图1：指令来源与消费者地图，放在整体介绍之后。
- 图2：provider→catalog→选择→加载时序图，放在首次关键数据或装配说明处。
- 图3：同名候选与 Scope 选择图，放在核心执行与数据交接处。
- 图4：缓存失效、来源失败与取消分支图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 企业 SOP Skill 的 provider 与加载示例，附来源选择和指令进入 Session 的流程。 核对同名选择、catalog/正文分离、来源变更及取消；说明结果作用域。

**范围边界：** 指令加载和工具执行授权分别研究；invocation policy 不等于企业认证。

<a id="article-19"></a>

### 19. 一个设置怎样真正生效：表单、patch 写回与实例更新

**定位：** M02 配置与扩展管理 · R03 · 既有源码深化。

**目标文件：** `articles/19-settings-config-writeback.md`

**中心问题：** 用户修改一个设置后，磁盘配置和运行实例分别发生了什么？

**前置阅读：** [00](../articles/00-config-loading-startup.md)、[01](../articles/01-plugin-lifecycle.md)、[02](../articles/02-deployment-evolution.md)；前置专题：无新增专题依赖。

**重点数据与对象：** 表单 descriptor、entry id 与 revision；raw / inherited / override / effective 值；secret 标记、字段操作与 volatile references。

**章节大纲：**

1. **整体地图：设置页面与运行配置之间有哪些交接。** 从用户修改到持久 patch 和 live 实例，分别建立保存、刷新与生效的观察点。
2. **表单生产：Config schema 与 volatile 字段。** 解释 Settings 如何读取有效 Entry、构造表单、确定可编辑范围及产生 revision。
3. **值的来源：raw、inherited、override 与 effective。** 在编辑前说明字段继承、表达式、secret 脱敏和保留，避免把页面值直接当作原始配置。
4. **写入入口：update、replace、mutate 与 reset。** 逐项解释字段操作、revision 冲突和继承恢复；说明这里的编辑算法与 patch 组合算法的交接。
5. **配置写回：config-editor 怎样维护用户 patch。** 追踪 Entry 身份定位、必要配置保留和磁盘提交，说明写入结果交给谁应用。
6. **运行生效：Entry/Fiber 更新与失败状态。** 沿刷新和 volatile 分支追踪新值；区分磁盘已保存、校验失败、实例保留和重建。
7. **开发示例与验证：给业务插件增加设置表单。** 验证正常保存、两端并发编辑、secret 保留、reset 和无效候选，不只展示成功页面。
8. **工程心得：设置接口应表达来源、并发与生效状态。** 结合正文解释企业后台需要提供什么事实，避免用一个成功提示承担所有阶段。

**源码研究入口：**

- [packages/settings/settings/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/settings/settings/src/index.ts)
- [packages/boot/config-editor/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/boot/config-editor/src/index.ts)
- [packages/api/settings-controller/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/settings-controller/src/index.ts)

**四图安排：**

- 图1：设置→持久 patch→运行实例整体图，放在整体介绍之后。
- 图2：schema 与各类配置值的对应图，放在首次关键数据或装配说明处。
- 图3：revision 检查和写回时序图，放在核心执行与数据交接处。
- 图4：volatile、重建与失败状态图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 可配置业务插件的设置与写回示例，附字段值、raw config、patch 和实例的交接图。 验证正常保存、陈旧 revision、secret 保留及失败边界；区分保存与运行生效。

**范围边界：** Settings 字段编辑与 patch 整个 config 覆盖各有契约，不混为同一种 merge。

<a id="article-20"></a>

### 20. 扩展包如何进入运行系统：安装、启停、移除与恢复边界

**定位：** M02 配置与扩展管理 · R04 · 既有源码深化。

**目标文件：** `articles/20-plugin-package-management.md`

**中心问题：** 一个扩展包从安装到启用、移除，经过哪些提交和清理边界？

**前置阅读：** [00](../articles/00-config-loading-startup.md)、[01](../articles/01-plugin-lifecycle.md)、[02](../articles/02-deployment-evolution.md)、[10](../articles/10-security.md)；前置专题：R03。

**重点数据与对象：** manifest / lockfile / bundle 选择；包操作请求、阶段结果与 profile 写锁；RuntimeResolution、Entry/Fiber 与包管理进程。

**章节大纲：**

1. **整体地图：安装、选择和激活是怎样连接的。** 建立包文件、保存的 bundle 选择和运行树之间的关系，解释管理操作对共享 profile 的影响。
2. **管理入口：CLI、服务与 UI 怎样进入共同操作。** 追踪请求参数、审批边界、launcher 事实和执行环境，说明业务界面应调用哪一层。
3. **准备阶段：spec 检查、registry 与兼容性。** 核对检查顺序、候选来源与超时，将待安装包信息交回操作入口。
4. **安装阶段：profile 写锁与包管理子进程。** 说明 manifest/lockfile 保存、输出、取消、进程树及异常退出处理。
5. **启停阶段：bundle 选择、解析表发布与 HMR。** 沿配置重组解释何时当前实例变化，何时仍需要重启，怎样等待撤销的资源。
6. **移除与失败：按阶段解释保留和恢复。** 分别分析包操作失败、验证失败、激活失败和卸载失败，建立恢复范围矩阵。
7. **开发示例与验证：管理一个教学 bundle。** 完成安装、禁用、启用、移除，以及取消和失败测试；记录保存与运行事实。
8. **工程心得：包管理是多阶段操作协议。** 由锁、进程和提交点推导管理服务设计，明确 Host 插件代码与安装脚本的信任责任。

**源码研究入口：**

- [packages/boot/plugin-manager/src/operations.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/boot/plugin-manager/src/operations.ts)
- [packages/boot/plugin-manager/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/boot/plugin-manager/src/index.ts)
- [packages/boot/app-boot/src/profile.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/boot/app-boot/src/profile.ts)

**四图安排：**

- 图1：安装/选择/激活的对象关系图，放在整体介绍之后。
- 图2：管理入口与包操作时序图，放在首次关键数据或装配说明处。
- 图3：bundle 变更到运行树更新图，放在核心执行与数据交接处。
- 图4：失败阶段与恢复范围矩阵图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 教学 bundle 的安装/启停/移除案例，附阶段结果和恢复矩阵。 分别验证保存状态、安装状态、激活状态；失败和取消后清理包管理进程。

**范围边界：** 管理操作涉及 Host 代码和安装脚本；配置恢复不等于包目录及业务副作用的全局回滚。

<a id="article-21"></a>

### 21. 从后端服务到浏览器面板：一个完整 DSH 插件的实现链

**定位：** M03 前后端与系统接入 · R05 · 既有源码深化。

**目标文件：** `articles/21-fullstack-plugin-development.md`

**中心问题：** 一个业务功能如何从 Host 服务进入浏览器，并在卸载时完整退出？

**前置阅读：** [00](../articles/00-config-loading-startup.md)、[01](../articles/01-plugin-lifecycle.md)、[16](../articles/16-interaction-deliverables.md)；前置专题：R01、R03。

**重点数据与对象：** dsh.client 与 Web boot graph；Remote 声明、descriptor 与 Context lookup；UI Slot、store、事件与挂载寿命。

**章节大纲：**

1. **整体地图：一个业务功能经过哪些构建与运行环境。** 把 Host 服务、Remote API、Client 插件和 UI 展示连接起来，说明各自的部署和执行责任。
2. **包声明与产物：dsh.client、exports 和双端构建。** 解释 metadata 与源码/产物的对应关系，指出类型生成和浏览器 bundle 的准备顺序。
3. **浏览器装配：Host Loader 到 Client module graph。** 追踪扫描、manifest、脚本交付和 Client 激活，说明动态变化怎样更新模块贡献。
4. **业务调用：Remote 声明到 Gateway 派发。** 解释生成契约、receiver/Context 定位、参数、结果和错误，回到 Client 消费者。
5. **界面装配：Slots、store 与事件订阅。** 追踪注册、状态生产、React 消费和用户交互，说明界面贡献如何跟随 Context 生命周期。
6. **长连接与撤销：重连、取消和卸载。** 分别说明 carrier 变化、业务流、保留句柄和挂载退出，避免把连接恢复当作业务操作重做。
7. **开发示例与验证：业务服务与查询面板。** 从包配置到构建和实际浏览器展示，验证正常调用、错误、断线、取消及插件卸载。
8. **工程心得：功能边界应贯穿类型、传输与展示。** 从两端贡献的寿命总结扩展方式，并说明需要一起重建和复核的产物。

**源码研究入口：**

- [packages/client/modules/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/client/modules/src/index.ts)
- [packages/api/gateway/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/gateway/src/index.ts)
- [packages/client/ui-slots/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/client/ui-slots/src/index.ts)
- [docs/development.md](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/docs/development.md)

**四图安排：**

- 图1：Host/Remote/Client/UI 整体地图，放在整体介绍之后。
- 图2：Loader→boot graph→Client 装配图，放在首次关键数据或装配说明处。
- 图3：类型生成与业务调用交接图，放在核心执行与数据交接处。
- 图4：重连、状态消费和卸载图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 业务服务＋Remote API＋Client 插件＋UI 面板的完整样例。 正常调用与展示；断线/取消后的正确状态；卸载后调用和展示资源撤销。

**范围边界：** 实例须完成类型生成和 Client 构建；源码可调用不等于浏览器产物可用。

<a id="article-22"></a>

### 22. 让业务系统驱动 DSH：SDK、ACP 与 Web 的入口选择

**定位：** M03 前后端与系统接入 · R06 · 既有源码深化。

**目标文件：** `articles/22-sdk-acp-web-integration.md`

**中心问题：** 企业应用应通过哪种入口创建 Session 并驱动同一运行内核？

**前置阅读：** [00](../articles/00-config-loading-startup.md)、[03](../articles/03-agent-loop.md)、[06](../articles/06-state-persistence.md)、[11](../articles/11-autonomy.md)、[16](../articles/16-interaction-deliverables.md)；前置专题：R01。

**重点数据与对象：** 入口请求、Session id 与运行 handle；协议结果、审批、事件与取消；SDK 子进程、连接和调用方寿命。

**章节大纲：**

1. **整体地图：三种入口怎样接到执行内核。** 给出适用场景和能力对照，区分启动配置、创建会话和提交任务。
2. **SDK 主线：配置 profile 并建立子进程通道。** 追踪参数、patch、stdio 协议、readiness 和子进程所有权。
3. **Session 主线：创建、恢复与输入接纳。** 沿 Client→Server→业务入口说明身份、结果和历史来源，把接纳返回值接回调用方。
4. **任务推进：事件订阅、审批与完成观察。** 解释消息、状态、事件和结束结果分别表示什么；将人类决策交回正确请求。
5. **ACP 与 Web 支线：各自适配什么契约。** 分别建立入口到公共业务服务的路径，核对能力差异，而非推定接口一一等价。
6. **取消与关闭：输入、Session、连接和进程。** 解释调用方中止时谁收到 signal、谁等待结算、哪些资源需要显式关闭。
7. **开发示例与验证：同一任务的入口对比。** 实现一个 SDK 集成，配合协议能力矩阵验证正常、审批、取消、恢复和客户端退出。
8. **工程心得：集成方式应跟随任务和资源归属。** 给出选择依据和生命周期要求，避免以协议连通替代业务完成验证。

**源码研究入口：**

- [packages/sdk/client/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/sdk/client/src/index.ts)
- [packages/sdk/server/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/sdk/server/src/index.ts)
- [packages/acp/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/acp/README.md)
- [packages/api/session-controller/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/session-controller/src/index.ts)

**四图安排：**

- 图1：SDK/ACP/Web 与执行内核关系图，放在整体介绍之后。
- 图2：SDK 子进程与 Session 创建时序图，放在首次关键数据或装配说明处。
- 图3：接纳、审批、事件和完成语义图，放在核心执行与数据交接处。
- 图4：取消与关闭的所有权图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 同一教学任务的入口对比及一个可运行 SDK 集成示例。 核对接纳与完成、正常结果、审批/取消和调用方退出；记录子进程清理。

**范围边界：** 协议能力逐项核对，不假定 SDK、ACP 与 Web 的所有操作完全等价。

<a id="article-23"></a>

### 23. 一个 MCP server 怎样成为 Agent 能力：连接、发现与重连

**定位：** M04 外部能力与程序执行 · R07 · 既有源码深化。

**目标文件：** `articles/23-mcp-connection-lifecycle.md`

**中心问题：** 远端能力如何变成本地可见、可调用且有生命周期的工具与资源？

**前置阅读：** [07](../articles/07-tool-runtime.md)、[08](../articles/08-reliability.md)、[10](../articles/10-security.md)；前置专题：R01。

**重点数据与对象：** server 配置与连接 generation；远端工具 definition、public name 和 schema；resources/instructions 与注册 disposer。

**章节大纲：**

1. **整体地图：连接不是能力加载的终点。** 先说明 connection、工具、resources 和 instructions 分别接入哪些本地服务。
2. **启动入口：stdio/HTTP transport 与 readiness。** 追踪配置校验、执行环境、transport 建立、初始发现和启动结果。
3. **工具发现：远端定义到本地注册。** 解释命名、schema 转换、候选准备和注册集合更新，指出 prepare 与应用的边界。
4. **工具调用：本地 ToolRuntime 到远端请求。** 沿参数、signal、timeout 和结果转换进入远端，再回到本地结算。
5. **资源与指令：独立消费者与作用域。** 追踪 resources 发现/读取和 server instructions 的 prompt 注册，明确各自寿命和权限边界。
6. **运行变化：重连、重新发现与 dispose。** 解释代际替换、旧注册撤销、正在执行的请求和退出等待；核对失败状态。
7. **开发示例与验证：受控 server 的完整生命周期。** 验证正常调用、断线、能力变化、取消和卸载，单独观察远端写入效果。
8. **工程心得：连接状态、能力状态与业务效果分别确认。** 从发现和重连机制提炼企业 connector 的可观察状态及外部幂等责任。

**源码研究入口：**

- [packages/mcp/mcp-client/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/mcp/mcp-client/src/index.ts)
- [packages/mcp/mcp-client/src/connection.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/mcp/mcp-client/src/connection.ts)
- [packages/mcp/mcp-client/src/tools.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/mcp/mcp-client/src/tools.ts)
- [packages/mcp/mcp-resources/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/mcp/mcp-resources/src/index.ts)

**四图安排：**

- 图1：连接、工具、resources 与 instructions 地图，放在整体介绍之后。
- 图2：初始连接与能力注册时序图，放在首次关键数据或装配说明处。
- 图3：本地到远端调用及取消图，放在核心执行与数据交接处。
- 图4：connection generation 与撤销图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 受控 MCP server 的连接与调用样例，附连接代际和注册生命周期。 验证正常调用、断线/重新发现、取消与卸载；明确远端副作用是否可确认。

**范围边界：** MCP connection、instructions 和工具注册不替代资源授权或远端幂等协议。

<a id="article-24"></a>

### 24. 模型程序如何受控执行：PTC、bindings 与内部工具调用

**定位：** M04 外部能力与程序执行 · R08 · 既有源码深化。

**目标文件：** `articles/24-ptc-program-execution.md`

**中心问题：** 模型程序如何通过 bindings 调用工具，并返回可解释的结果？

**前置阅读：** [07](../articles/07-tool-runtime.md)、[08](../articles/08-reliability.md)、[09](../articles/09-concurrency.md)、[10](../articles/10-security.md)、[12](../articles/12-budgets.md)；前置专题：R01。

**重点数据与对象：** presentation 模式和生成 bindings；PtcRunRequest / PtcRunResult；transport 执行、内部调用、输出和运行进程。

**章节大纲：**

1. **整体地图：从工具列表到程序式调用。** 解释 native/ptc/both 的请求呈现，以及 runtime、工具和 Session 的分工。
2. **绑定阶段：可见工具怎样形成 SDK/bindings。** 追踪工具选择、名称与 schema、绑定快照和程序入口，说明哪些内容只服务当前执行。
3. **请求阶段：run_code 怎样交给 PTC runtime。** 先展示请求/结果契约，再分析验证、runtime 选择和生命周期交接。
4. **执行阶段：运行进程、协议与 host bindings。** 追踪程序、异步内部调用、返回值和输出，区分运行后端与工具派发职责。
5. **内部工具：授权、超时、并发和结果提交。** 沿 binding 回到真实工具入口，核对权限仍在哪里判断以及内部调用如何归属。
6. **异常与清理：程序失败、工具失败和取消。** 逐项解释错误进入哪份结果、signal 怎样传播、子进程怎样排空和退出。
7. **开发示例与验证：一次程序调用两个受控工具。** 验证正确结果、拒绝访问、异常区分和取消；性能比较仅在实际测量后给结论。
8. **工程心得：程序执行需要保留能力与结果边界。** 由 bindings 和工具入口总结批处理适用条件，说明扩展运行后端需要履行的契约。

**源码研究入口：**

- [packages/core/agent-tool-presentation/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent-tool-presentation/src/index.ts)
- [packages/ptc-runtime/ptc-runtime/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/ptc-runtime/ptc-runtime/src/index.ts)
- [packages/ptc-runtime/ptc-runtime-node/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/ptc-runtime/ptc-runtime-node/src/index.ts)

**四图安排：**

- 图1：presentation→program→tools 整体图，放在整体介绍之后。
- 图2：bindings 与请求数据结构图，放在首次关键数据或装配说明处。
- 图3：程序进程和内部工具调用图，放在核心执行与数据交接处。
- 图4：错误归属、取消与清理图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 调用两个受控工具的程序示例，附内部调用链、失败和取消记录。 验证内部工具授权；程序/工具错误可区分；取消后清理进程。

**范围边界：** PTC runtime 与 Session/工具语义分别核对，不预设性能提升幅度。

<a id="article-25"></a>

### 25. 从 Agent 执行到任务编排：Workflow、Schedule 与 Hooks

**定位：** M05 任务编排与企业集成 · R09 · 既有源码深化。

**目标文件：** `articles/25-workflow-schedule-hooks.md`

**中心问题：** 任务编排、定时触发和执行钩子各自负责哪一段运行过程？

**前置阅读：** [08](../articles/08-reliability.md)、[09](../articles/09-concurrency.md)、[11](../articles/11-autonomy.md)、[15](../articles/15-task-completion.md)；前置专题：R01、R08。

**重点数据与对象：** workflow 请求、run、子任务与结果；schedule 触发记录及寿命；hook 请求、响应、来源与执行 Context。

**章节大纲：**

1. **整体地图：编排、触发和钩子各解决什么问题。** 明确三种机制的角色和调用来源，给出边界矩阵，不构造不存在的统一主线。
2. **Workflow 主线：脚本怎样成为一个 run。** 先解释输入与结果结构，再追踪校验、执行引擎、父子归属和结果交接。
3. **子任务主线：并行、阶段、失败与清理。** 解释普通子任务失败与运行基础设施失败的差别，核对取消及等待。
4. **Schedule 支线：注册、触发和 owner 退出。** 追踪时间输入、触发消费、重复触发和撤销，并核实实际持久与重启行为。
5. **Hooks 支线：协议适配和控制权。** 分别追踪 Codex/Claude Code hook 的输入、执行与返回，核对来源与副作用边界。
6. **组合边界：恢复、取消与业务流程保证。** 比较三种机制的生命周期和提交点，说明企业调度或事务需要另外设计什么。
7. **开发示例与验证：一个可观察的任务编排。** 验证成功、普通失败、基础设施失败、取消、重复触发和 owner 退出。
8. **工程心得：触发成功、运行结算与业务完成分别记录。** 从各自主线推导编排系统需要保存的事实，避免用 Agent 结束替代业务验收。

**源码研究入口：**

- [packages/workflow/workflow/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/workflow/workflow/src/index.ts)
- [packages/workflow/workflow-ptc/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/workflow/workflow-ptc/src/index.ts)
- [packages/schedule/schedule/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/schedule/schedule/src/index.ts)
- [packages/hooks/hook-protocol/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/hooks/hook-protocol/src/index.ts)

**四图安排：**

- 图1：三种机制的职责地图，放在整体介绍之后。
- 图2：Workflow run 与子任务寿命图，放在首次关键数据或装配说明处。
- 图3：Schedule/Hook 独立入口图，放在核心执行与数据交接处。
- 图4：失败、持久性和恢复边界对照图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 任务编排示例与三种机制的寿命/恢复对照表。 核对普通失败、基础设施失败、取消、重复触发与 owner 退出；说明实际持久范围。

**范围边界：** 不预设 Schedule 是持久企业调度器，或 Workflow 有业务事务保证。

<a id="article-26"></a>

### 26. 把企业数据与远端操作接入 DSH：provider、授权与效果确认

**定位：** M05 任务编排与企业集成 · R10 · 源码深化与企业新增设计。

**目标文件：** `articles/26-enterprise-data-remote-execution.md`

**中心问题：** 业务数据、知识检索和远端执行怎样通过扩展接缝进入任务？

**前置阅读：** [07](../articles/07-tool-runtime.md)、[08](../articles/08-reliability.md)、[10](../articles/10-security.md)、[15](../articles/15-task-completion.md)、[16](../articles/16-interaction-deliverables.md)；前置专题：R01、R07、R11。

**重点数据与对象：** 能力定义、provider 与 consumer；主体/资源/凭据和业务输入；操作 id、回执、未知结果与产物记录（新增设计）。

**章节大纲：**

1. **业务场景与整体地图：从任务到企业资源。** 选定一条数据查询及业务写入主线，声明可信主体、资源、效果与交付要求。
2. **既有接缝：fs、shell、subprocess 与 Workspace。** 核实接口、provider 挂载、consumer 及释放责任，确定可复用的调用边界。
3. **企业数据接入：connector 与知识检索的新增契约。** 设计查询、来源、授权和返回数据边界；知识检索只作为可选接入，不写成默认能力。
4. **远端执行接入：位置、身份与执行环境。** 需要时单列后端协议和凭据传递，解释取消、路径映射与产物怎样跨环境交接。
5. **业务效果确认：幂等、回执与未知结果。** 追踪请求到外部效果及确认，说明断线和再次执行时如何避免重复写入。
6. **恢复与交付：重新授权、结果核验与产物保存。** 区分运行恢复和外部事务，保存可确认事实以及无法确认的状态。
7. **开发示例与验证：企业查询和一次可确认写入。** 在受控系统验证权限、写入确认、断线、取消、重复操作与交付；记录 mock 范围。
8. **工程心得：Agent 结果需要连接业务事实。** 解释现有 Harness 契约的复用价值与新增责任，给出接入边界和适用条件。

**源码研究入口：**

- [packages/fs/fs/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/fs/fs/src/index.ts)
- [packages/shell/shell/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/shell/shell/src/index.ts)
- [packages/subprocess/subprocess/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/subprocess/subprocess/src/index.ts)
- [packages/workspace/workspace/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/workspace/workspace/src/index.ts)

**四图安排：**

- 图1：任务→企业资源→交付整体图，放在整体介绍之后。
- 图2：既有 provider 与新增 connector 边界图，放在首次关键数据或装配说明处。
- 图3：业务写入与回执时序图，放在核心执行与数据交接处。
- 图4：断线、未知结果、恢复与幂等图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 企业数据查询＋一次可确认业务写入的案例；需要远端执行时单列 provider 协议。 受控外部系统验证权限、幂等/未知结果、取消与交付；显式记录 mock 范围。

**范围边界：** provider 契约是源码研究；企业 connector、RAG 或远端后端是新增设计，不描述为默认能力。

<a id="article-27"></a>

### 27. 企业 Agent 的身份边界：可信入口、凭据与租户资源授权

**定位：** M06 身份治理与产品交付 · R11 · 源码深化与企业新增设计。

**目标文件：** `articles/27-identity-credentials-tenancy.md`

**中心问题：** 可信主体如何关联 Agent、Session、Workspace、模型、凭据和业务资源？

**前置阅读：** [06](../articles/06-state-persistence.md)、[09](../articles/09-concurrency.md)、[10](../articles/10-security.md)、[13](../articles/13-observability.md)；前置专题：R01、R06。

**重点数据与对象：** 现有请求信任、Context lookup 与资源归属；principal / tenant / policy（新增设计）；凭据句柄、授权决定与审计记录（逐项核实/设计）。

**章节大纲：**

1. **整体地图：哪些身份来自可信入口。** 定义企业主体、租户、任务和资源边界，列出单用户、团队与多租户部署的不同要求。
2. **已有边界：请求信任与 Context/Session 定位。** 盘点真实实现的检查位置和作用域，说明当前保护能够支持什么证据。
3. **凭据链：保存、读取、消费与撤销。** 追踪凭据服务和本地存储保护，确定模型、连接和业务工具消费秘密的位置。
4. **新增身份契约：principal、tenant 与资源归属。** 明确企业认证入口、映射和策略接口，分别标注源码事实与新增设计。
5. **授权执行链：可见性、派发与资源操作。** 沿具体任务放置检查，解释列表过滤、工具调用和数据返回前授权的不同责任。
6. **恢复与 delegation：身份重新确认和缓存处理。** 说明恢复、子任务、后台任务及撤权后再次执行的设计，避免继承过期授权。
7. **开发示例与验证：隔离两个业务主体的资源访问。** 建立越权、跨租户、凭据泄漏、撤权、恢复与子任务验证矩阵，并记录未实现项。
8. **工程心得：隔离承诺必须由具体执行边界支持。** 从主体和资源链总结部署选择，区分 scoped 可见性、资源授权和进程隔离。

**源码研究入口：**

- [packages/client/connection/src/api-request-trust.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/client/connection/src/api-request-trust.ts)
- [packages/api/gateway/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/api/gateway/src/index.ts)
- [packages/credentials/credentials/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/credentials/credentials/src/index.ts)
- [packages/credentials/credentials-local/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/credentials/credentials-local/src/index.ts)

**四图安排：**

- 图1：主体→Agent→Session→资源关系图，放在整体介绍之后。
- 图2：请求信任与凭据消费图，放在首次关键数据或装配说明处。
- 图3：企业新增授权检查位置图，放在核心执行与数据交接处。
- 图4：恢复、子任务和撤权后的授权图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 企业授权链设计、资源归属矩阵及越权/撤权测试案例。 验证跨租户拒绝、凭据不越界、恢复与子任务重新授权；区分进程与资源隔离。

**范围边界：** 承接企业报告已有责任划分继续深化，不宣称 DSH 当前已有完整多租户平台。

<a id="article-28"></a>

### 28. 从源码到企业发行包：构建、安装、升级与验证

**定位：** M06 身份治理与产品交付 · R12 · 既有源码深化。

**目标文件：** `articles/28-build-package-distribution.md`

**中心问题：** 二次开发成果怎样从源码成为目标环境真正可运行的产品？

**前置阅读：** [00](../articles/00-config-loading-startup.md)、[02](../articles/02-deployment-evolution.md)、[14](../articles/14-evaluation.md)；前置专题：R04、R05、R06。

**重点数据与对象：** Host/Client faces 与生成产物；package exports、依赖及 native 产物；profile/bundle、安装环境与版本/验证矩阵。

**章节大纲：**

1. **整体地图：哪些产物组成一份可运行发行包。** 说明源码、生成类型、Host/Client bundle、原生依赖和运行配置之间的关系。
2. **构建主线：Host、Typert 与 Client 的依赖顺序。** 追踪构建入口、输入输出和后续 consumer，解释工作区源码解析与发布产物解析。
3. **扩展包主线：exports、依赖与打包内容。** 核对教学包实际包含的入口、类型和 Client 文件，验证离开 monorepo 后的依赖解析。
4. **应用产物：Web、Desktop 与 SDK 的装配差异。** 逐项说明运行入口、profiles、bundles、资源和平台相关依赖，避免将产物混用。
5. **安装验证：从干净目录和目标产物启动。** 验证初始配置、能力激活、调用、退出和资源释放，记录目标平台及凭据限制。
6. **升级验证：旧数据、兼容与失败处理。** 建立配置、Session、插件版本及产物矩阵，核对排空、失败恢复和可承诺范围。
7. **开发示例与验证：打包并安装教学扩展。** 给出可复现命令、产物清单和正常/异常启动证据，将阶段构建结果汇总为发行验收。
8. **工程心得：发行能力应由安装产物证明。** 由构建与实际消费关系总结升级检查方法，说明源码测试、安装验证和平台覆盖的各自范围。

**源码研究入口：**

- [docs/development.md](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/docs/development.md)
- [package.json](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/package.json)
- [scripts/build.ts](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/scripts/build.ts)
- [apps/desktop/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/apps/desktop/README.md)

**四图安排：**

- 图1：源码→构建→发行产物地图，放在整体介绍之后。
- 图2：Host/Typert/Client 构建依赖图，放在首次关键数据或装配说明处。
- 图3：Web/Desktop/SDK 产物与入口图，放在核心执行与数据交接处。
- 图4：安装、升级、退出与失败验证矩阵图，放在异常、恢复或卸载分析处。

**样例与验证任务：** 教学扩展的打包与安装记录，附产物依赖图和目标环境矩阵。 从产物启动；记录目标平台、依赖、退出与升级的实际验证限制。

**范围边界：** 完整发行研究最后汇总；每个样例所需构建和类型生成从一开始执行。

## 4. 跨专题配套文档

配套文档拟保存在 `appendices/`；它们是持续维护的研究材料，与逐篇文章交付分开记录。当前仅列清单和大纲，不创建占位文件。

|标识|拟定文档|拟定文件名|核心用途|
|---|---|---|---|
|A01|扩展契约矩阵|`extension-contract-matrix.md`|定位扩展挂载、生命周期及兼容责任。|
|A02|完整扩展样例说明|`end-to-end-extension-example.md`|串联业务工具、服务、界面、设置和 bundle。|
|A03|改动影响与回归矩阵|`change-impact-regression-matrix.md`|定位修改与升级后需重建、复核和验证的范围。|

### A01 扩展契约矩阵

1. 能力分类与使用场景：说明定义、provider 和 consumer 的分工。
2. 挂载与作用域矩阵：Host/Agent、Context/Scope、依赖及配置入口。
3. 输入、输出与提交点：公开结构、事件、持久事实和状态转换。
4. 更新和释放责任：重新配置、撤销、在途任务和 owner 退出。
5. 兼容与验证：消费者、类型/构建依赖、源码锚点及可执行检查。

### A02 完整扩展样例说明

1. 业务场景与验收：选定最小任务、授权范围、结果和交付物。
2. 包与目录：业务工具、Host 服务、Remote、Client、设置与 bundle 的实际文件。
3. 配置与启动：profile、patch、构建产物和启动命令。
4. 正常运行链：创建 Agent、交互、工具执行、结果及展示。
5. 生命周期链：设置变更、取消、断线、卸载与资源清理。
6. 验证记录：类型、构建、运行、安装及目标环境；保留失败和限制。

### A03 改动影响与回归矩阵

1. 改动类型：接口、配置、协议、持久数据、依赖和运行后端。
2. 影响传播：定义→provider→consumer→产物→部署场景。
3. 重建清单：Host、Typert、Client、native 和发行产物。
4. 回归清单：正常、失败、取消、恢复、并发、撤权与卸载。
5. 版本同步：固定新旧 SHA，核实移动/变化/消失的契约与证据。
6. 放行证据：实际命令、退出码、平台、验证限制与未完成项。

## 5. 推荐编写顺序与交付标准

|阶段|推荐安排|阶段成果|
|---|---|---|
|第一阶段：基础装配|17 → 18；19 可独立推进|正确创建 Agent、接入指令并解释设置生效。|
|第二阶段：完整开发链|21、22、23；20 承接19|可调用的服务、界面、系统入口和外部工具。|
|第三阶段：执行与编排|24 → 25|可观察、可取消的程序与子任务链。|
|第四阶段：企业与发行|满足27身份设计后推进26；28汇总产物验证|企业资源接入、业务效果确认和实际安装证据。|

完成标准包括：文章围绕中心问题形成连续源码解读；关键结构和状态有固定提交证据；四图与正文对应；样例在声明的范围内可运行；正常与代表性异常结果有命令及日志；心得来自正文；未验证部分如实保留。

本文件保留初始章节与验收要求。17—28篇已逐篇建立计划、摘录、图示与检查记录；源码研究已完成，真实外部系统、SSO、完整浏览器和跨平台发行等未验收项在文章及配套矩阵中单独保留。大纲中的目标不自动成为实现或测试结论。

[补充研究路线图](supplementary-research-plan.md) · [专栏目录](../articles/README.md) · [企业二次开发报告](../04-enterprise-harness-practices.md)
