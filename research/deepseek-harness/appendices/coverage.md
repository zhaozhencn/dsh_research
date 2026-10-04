# 研究覆盖与排除范围

全量指全部tracked目录及workspace成员盘点，不是逐行阅读。采用四档：关键实现深读（选段）、实现／接口选读、配置／说明概览、仅清单盘点。每档与实际运行测试分列。由manifest得出的description保留原文，并标为目录元数据；不可用它代替代码执行证明。

原始range日志记录请求阅读的文件和区间，部分工具输出曾截断，因此**不能当作逐行已读计数或覆盖率**。阅读深度由实际掌握的关键实现标记，未宣称整个大文件都深读。旧版盘点漏了5个native成员，最终已补齐并与pnpm递归清单对照：341成员＋根工具项目＝342。

## 顶层目录与处理方式

|目录|tracked文件数|处理／原因|
|---|---:|---|
|`"snapshots/`|1|完整tracked盘点；非核心材料未逐文件阅读|
|`.agents/`|3632|维护规则及相关决策按需追踪；不把说明当执行事实|
|`.claude/`|1|辅助配置盘点，非runtime核心|
|`.github/`|53|配置文件盘点，未执行完整CI|
|`apps/`|1121|CLI关键启动深读；Web/Desktop manifest与架构说明概览，未实际构建／启动UI|
|`benchmarks/`|43|完整盘点；本次选读 continuation benchmark 说明，未执行性能测量|
|`docs/`|597|architecture及本次测试分层、遥测、记忆、格式说明选读；不全读生成catalog|
|`native/`|79|AGENTS/README/build与lease消费追踪；只本机编译|
|`packages/`|6847|全包清单＋核心深读＋29 个选定仓库测试文件|
|`patches/`|7|补丁列表盘点，相关依赖行为按需；未审计全部补丁|
|`python/`|40|SDK启动接口选读、runtime manifest；未安装wheel或跑Pythontests|
|`scripts/`|336|工具／构建／alias配置选读；大量生成器只盘点|
|`snapshots/`|1297|目录盘点，回归fixture按需；未运行完整snapshot|
|`vendor/`|76|清单、上游pin、本地Cordis/Loader/Include生命周期追踪；未通读全部第三方源码|
|`website/`|32|manifest／锁版本；网站内容与静态资源排除深读|

根文件：package.json、pnpm-workspace.yaml、锁文件、tsconfig.base/host/client、vitest配置、AGENTS、README等用于基线与构建／执行契约核验。锁文件全量保留、按importer查关键依赖，不宣称逐行阅读。

## 子系统职责和分包数量

|分组|包数|职责归纳|
|---|---:|---|
|`packages/acp`|1|自动化协议接入|
|`packages/api`|9|Host Remote 控制与传输|
|`packages/attachment`|2|消息附件与读取|
|`packages/boot`|5|应用组装／加载／配置／插件管理|
|`packages/browser-use`|1|浏览器操作能力|
|`packages/bundle`|6|产品配置分发与profile|
|`packages/client`|63|Client连接、状态、UI组件及slots|
|`packages/compaction`|5|模型surface压缩与结果修剪|
|`packages/computer-use`|1|桌面操作能力|
|`packages/context`|6|模型上下文贡献|
|`packages/core`|8|Agent、Session、tools、scope与prompt基础|
|`packages/credentials`|5|凭据与账户接入|
|`packages/deliverables`|2|产物呈现／工作区变化|
|`packages/document`|1|文档转换|
|`packages/experimental`|24|实验执行器／协作／UI等|
|`packages/extensions`|4|额外开发与管理工具|
|`packages/feedback`|2|用户反馈|
|`packages/fs`|7|文件系统定义／provider／工具|
|`packages/goal`|4|目标及预算驱动|
|`packages/guard`|2|执行拦截与保护策略|
|`packages/hooks`|3|外部Agent钩子协议|
|`packages/host`|9|Host运行载体能力|
|`packages/identity`|1|身份事实|
|`packages/interaction`|5|审批／命令／提问|
|`packages/jobs`|3|任务服务／本地provider／工具|
|`packages/llm`|9|模型、adapter、retry与token估算|
|`packages/lsp`|3|语言服务协议|
|`packages/mcp`|2|MCP工具／资源接入|
|`packages/plan`|1|计划能力|
|`packages/preset`|3|声明式Agent能力组合|
|`packages/ptc-runtime`|2|程序化工具执行Runtime|
|`packages/sandbox`|4|策略定义与平台confinement|
|`packages/schedule`|2|调度与工具|
|`packages/sdk`|3|SDK与stdio服务|
|`packages/session`|20|持久化、投影、格式与辅助状态|
|`packages/session-query`|4|查询／导出／数据库索引|
|`packages/settings`|1|运行配置服务|
|`packages/shell`|10|Shell定义／provider／工具|
|`packages/skill`|6|技能注册／加载／工具|
|`packages/spill`|3|大输出存放及策略|
|`packages/ssh`|4|远端能力provider|
|`packages/storage`|4|通用存储定义／domain／provider|
|`packages/subagent`|10|子Agent生命周期／provider／工具|
|`packages/subprocess`|3|进程管理能力|
|`packages/telemetry`|1|观测接入|
|`packages/terminal`|3|持久终端能力|
|`packages/test-support`|7|验证辅助与mock|
|`packages/todo`|1|待办工具|
|`packages/typert`|4|类型化Remote契约／代码生成|
|`packages/util`|17|共享辅助机制|
|`packages/web`|6|搜索／抓取定义／provider／工具|
|`packages/webhook`|2|外部事件入口|
|`packages/workflow`|4|脚本工作流／provider／工具|
|`packages/workspace`|1|工作区能力|

## 逐workspace覆盖表

关键文件列是源码定位入口；catalog-only条目未因此升级为已读源码。验证列写“未运行”即未独立执行该包测试；消费者测试也不意味着该包全部接口验证。章节归属允许多个篇章。

|模块／包|职责来源（manifest description）|关键文件|阅读深度|运行验证|篇章|遗留范围|
|---|---|---|---|---|---|---|
|`apps/cli`<br>`@deepseek-ai/dsh`|dsh CLI: profile launch, plugin management, and configuration inspection|`src/bin.ts；src/profile-boot.ts`|关键实现深读（选段）|未独立运行|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`apps/desktop`<br>`@deepseek-ai/dsh-desktop`|Electron desktop shell for a bundled dsh runtime and external plugins|`README.md`|配置／说明概览|未独立运行|1（盘点）|实现与运行行为未深核|
|`apps/desktop-host`<br>`@deepseek-ai/dsh-desktop-host`|Private Node-mode host process for the Electron desktop application|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`apps/web`<br>`@deepseek-ai/dsh-web-frontend`|Web application entry: vite build over the @deepseek-ai/dsh-client-web shell library; dist/ served by apps/cli's dsh web|`package.json`|配置／说明概览|未独立运行|1（盘点）|实现与运行行为未深核|
|`benchmarks`<br>`@deepseek-ai/dsh-benchmarks`||`agent-continuation/README.md`|配置／说明概览|未独立运行|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`native/system`<br>`@deepseek-ai/node-addon-system-workspace`||`README.md`|配置／说明概览|native build；V03 flock消费者验证|1（盘点）|实现与运行行为未深核|
|`native/system/packages/darwin-arm64`<br>`@deepseek-ai/node-addon-system-darwin-arm64`|Prebuilt POSIX flock Node-API binding for macOS arm64|`README.md`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`native/system/packages/darwin-x64`<br>`@deepseek-ai/node-addon-system-darwin-x64`|Prebuilt POSIX flock Node-API binding for macOS x64|`README.md`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`native/system/packages/entry`<br>`@deepseek-ai/node-addon-system`|Prebuilt system primitives: a Linux Landlock launcher and asynchronous POSIX flock through stable Node-API|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`native/system/packages/linux-arm64`<br>`@deepseek-ai/node-addon-system-linux-arm64`|Linux arm64 system binaries: static Landlock launcher and glibc/musl Node-API flock addons|`README.md`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`native/system/packages/linux-x64`<br>`@deepseek-ai/node-addon-system-linux-x64`|Linux x64 system binaries: static Landlock launcher and glibc/musl Node-API flock addons|`README.md`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/acp/acp`<br>`@deepseek-ai/dsh-acp`|Automation-only Agent Client Protocol server for driving DeepSeek Harness agents over JSON-RPC stdio|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/api/account-controller`<br>`@deepseek-ai/dsh-api-account-controller`|Expose safe account operations over authenticated Remote|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/api/gateway`<br>`@deepseek-ai/dsh-api-gateway`|Typert Remote Host dispatcher and Client API endpoint|`src/index.ts`|关键实现深读（选段）|未独立运行|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/api/job-controller`<br>`@deepseek-ai/dsh-api-job-controller`|Job Remote observation stream and the reference-counted client job-output service|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/api/remotes`<br>`@deepseek-ai/dsh-api-remotes`|Remote BFF assembly for application-selected Host capabilities|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/api/session-controller`<br>`@deepseek-ai/dsh-api-session-controller`|Session Remote commands, cold reads, and live control transport|`src/index.ts`|关键实现深读（选段）|V02|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/api/settings-controller`<br>`@deepseek-ai/dsh-api-settings-controller`|Remote owner for the configuration surfaces over the settings-domain seams|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/api/terminal-controller`<br>`@deepseek-ai/dsh-api-terminal-controller`|Session-owned interactive terminals with shell discovery, screen recovery and typed Remote control|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/api/workspace-controller`<br>`@deepseek-ai/dsh-api-workspace-controller`|Workspace Remote commands and reconnect-safe state transport|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/api/workspace-files`<br>`@deepseek-ai/dsh-api-workspace-files`|Workspace file service and Client resource provider: bounded reads, directory listing, and live metadata over the workspaceFiles Remote namespace|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/attachment/attachment`<br>`@deepseek-ai/dsh-attachment`|Durable immutable attachment storage seam for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/attachment/attachment-local`<br>`@deepseek-ai/dsh-attachment-local`|Private content-addressed DSH_HOME attachment storage|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/boot/app-boot`<br>`@deepseek-ai/dsh-app-boot`|Shared boot glue for the app bins: .env loading, fail-loud Loader guards, snapshot-aware config resolution, and the Loader boot sequence|`src/index.ts`|关键实现深读（选段）|V01|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/boot/cmdline`<br>`@deepseek-ai/dsh-cmdline`|Immutable command-line handoff from a dsh launcher to any app plugin that injects cmdlineArgs|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/boot/config-editor`<br>`@deepseek-ai/dsh-config-editor`|Persist plugin configuration through profile patches and Loader reconciliation|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/boot/hmr`<br>`@deepseek-ai/dsh-hmr`|Coordinated module and profile configuration hot reload|`src/index.ts`|关键实现深读（选段）|V02|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/boot/plugin-manager`<br>`@deepseek-ai/dsh-plugin-manager`|Current-profile plugin and bundle management shared by dsh CLI, Web and agent tools|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/browser-use/browser-use`<br>`@deepseek-ai/dsh-browser-use`|Exclusive named browser-use provider registration|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/bundle/acp-app`<br>`@deepseek-ai/dsh-acp-app`|The dsh ACP profile bundle: automation-only JSON-RPC stdio and process lifecycle over dsh-base|`src/index.ts`|配置／说明概览|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/bundle/base`<br>`@deepseek-ai/dsh-base`|The shared dsh core as a profile bundle: the first patch layer of base-backed profiles, inserting core rows over the empty profile root|`cordis.patch.yml`|配置／说明概览|未独立运行|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/bundle/headless`<br>`@deepseek-ai/dsh-headless`|The dsh one-shot bundle: a direct core Agent/Session runner over dsh-base with no Host, HTTP, or browser layer|`src/index.ts`|实现／接口选读|未独立运行|1/3|已选读接口的其余实现未全审|
|`packages/bundle/sdk-app`<br>`@deepseek-ai/dsh-sdk-app`|The dsh SDK profile bundle: stdio JSON-RPC serving and process lifecycle over dsh-base|`src/index.ts`|配置／说明概览|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/bundle/sdk-minimal`<br>`@deepseek-ai/dsh-sdk-minimal`|The standalone minimal SDK profile bundle: JSON-RPC, one DeepSeek adapter, persistent shell, and JSONL sessions|`src/index.ts`|配置／说明概览|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/bundle/web-app`<br>`@deepseek-ai/dsh-web-app`|The dsh browser-surface bundle: the web patch layer over dsh-base plus the runtime glue plugin (frontend dist serving, web-surface prompt, bash runtime variables, URL line)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/connection`<br>`@deepseek-ai/dsh-client-connection`|Authenticated RPC transport and generation lifecycle|`src/index.ts`|实现／接口选读|未独立运行|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/client/file-upload`<br>`@deepseek-ai/dsh-client-file-upload`|Agent-scoped browser file upload, streaming intake, and staged receipt service|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/hmr`<br>`@deepseek-ai/dsh-client-hmr`|Web client graph synchronization and rebuilt-bundle reload transport|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/locale`<br>`@deepseek-ai/dsh-client-locale`|Locale plugin: Host-backed preference, extensible language catalog, browser fallback, and typed built-in dictionaries|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/modules`<br>`@deepseek-ai/dsh-client-modules`|Client module system, dual-face: node half composes the __DSH_BOOT__ entry graph (incremental dsh.client scan, bundle route, index tap, webPlugins service); browser half is the lazy-CJS module table the vendored cordis Loader consumes as its internal seam|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/product-analytics`<br>`@deepseek-ai/dsh-client-product-analytics`|Desktop product event collection and authenticated Host reporting|`src/index.ts`|关键实现深读（选段）|未独立运行|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/client/resources`<br>`@deepseek-ai/dsh-client-resources`|Unified client resource model: protocol-registered providers turn URL addresses into live values, consumed through the useResource global standard hook|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/shortcuts`<br>`@deepseek-ai/dsh-client-shortcuts`|Application keyboard command registry and physical-key routing|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/store`<br>`@deepseek-ai/dsh-client-store`|React-free observable and snapshot-store contracts with the shared Zustand/Immer engine|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-agent-preset`<br>`@deepseek-ai/dsh-client-ui-agent-preset`|Agent-preset surfaces: the default for later sessions, this session's seat, and the composition editor|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-approval`<br>`@deepseek-ai/dsh-client-ui-approval`|Approval composer takeover over the scoped Remote Event waterfall|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-attachment`<br>`@deepseek-ai/dsh-client-ui-attachment`|Dynamic attachment presentation plugin for conversation input, message-image, and trajectory image slots|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-brand-official`<br>`@deepseek-ai/dsh-client-ui-brand-official`|Official DeepSeek Harness brand occupants for the Web client's sidebar slots|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-chat`<br>`@deepseek-ai/dsh-client-ui-chat`|Chat Conversation target, node definitions, renderers, and details surface|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-commands`<br>`@deepseek-ai/dsh-client-ui-commands`|Client command surface: global directory cache, '/' source, three command UI kinds, popupSelect registry|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-conversation`<br>`@deepseek-ai/dsh-client-ui-conversation`|Target-neutral Conversation assembly, shell, composer, queue, and view navigation|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-deliverables`<br>`@deepseek-ai/dsh-client-ui-deliverables`|Changed-files card with per-file comparison tabs, delivery cards, and clickable final-response file references for Web|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-directory-picker-browse`<br>`@deepseek-ai/dsh-client-ui-directory-picker-browse`|In-app directory browsing surface: the workspace directory-flow owner rendering the host's listing and creation primitives|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-directory-picker-native`<br>`@deepseek-ai/dsh-client-ui-directory-picker-native`|Native directory-picker surface: the renderless workspace directory-flow occupant driving the local Desktop or Host OS chooser|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-dockkit`<br>`@deepseek-ai/dsh-client-ui-dockkit`|Docking layout kit: split-tree engine with invertible operations, and the React components that render and drive it (zero cordis)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-goal`<br>`@deepseek-ai/dsh-client-ui-goal`|Session goal surface: GoalBar docked above the composer, read from the goal session projection|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-input-trigger`<br>`@deepseek-ai/dsh-client-ui-input-trigger`|Input trigger pipeline: '/' and '@' detection, candidate menu, pick routing to registered sources|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-jobs`<br>`@deepseek-ai/dsh-client-ui-jobs`|Session-header background-job list with on-demand streaming record panels|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-layout`<br>`@deepseek-ai/dsh-client-ui-layout`|Shell plugin: three-column AppFrame with drag handles, ctx.layout viewing-state service (navigation + panels)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-message-feedback`<br>`@deepseek-ai/dsh-client-ui-message-feedback`|The Web feedback surface: per-message Like/Dislike in the assistant-message action strip and the feedback dialog behind both ratings and /feedback, backed by the messageFeedback and sessionFeedback Host Remotes|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-model-selection`<br>`@deepseek-ai/dsh-client-ui-model-selection`|Model selection over the shared model catalog, Session projection, and session.selectModel|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-open-in-app`<br>`@deepseek-ai/dsh-client-ui-open-in-app`|Web "Open In..." controls: the Session-header split button opening the workspace directory in an installed application, and the document preview's default-application controls for one file|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-permission-presets`<br>`@deepseek-ai/dsh-client-ui-permission-presets`|Permission surfaces: a new-session default in General settings and a current-session /permission popup over the permissions projection|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-plan`<br>`@deepseek-ai/dsh-client-ui-plan`|Plan mode controls, persistent transcript plan cards, and sidebar Markdown previews|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-plugin-manager`<br>`@deepseek-ai/dsh-client-ui-plugin-manager`|Plugin management for the dsh web client: the sidebar Plugins panel installs, enables, disables, retries, and composes installed plugin packages|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-primitives`<br>`@deepseek-ai/dsh-client-ui-primitives`|Pure React atoms for the dsh web UI: controls, icons, markdown, and JSON inspectors (zero cordis)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-reference`<br>`@deepseek-ai/dsh-client-ui-reference`|Unified Web @file and @session reference source|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-renderer`<br>`@deepseek-ai/dsh-client-ui-renderer`|Browser UI renderer: React slot bindings, ctx.uiRenderer, and the assembled application root|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-schedule`<br>`@deepseek-ai/dsh-client-ui-schedule`|Host task management page and Session reminder catalog|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-session`<br>`@deepseek-ai/dsh-client-ui-session`|Session Controller adapter for React and session-scoped slots|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings`<br>`@deepseek-ai/dsh-client-ui-settings`|Settings domain base plugin: shared configuration forms and the canonical settings slot-type contract|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-account`<br>`@deepseek-ai/dsh-client-ui-settings-account`|Manage DeepSeek login and open Platform billing pages|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-agent-loop`<br>`@deepseek-ai/dsh-client-ui-settings-agent-loop`|Settings page of the agent loop on the dsh web client's Plugins page: the parallel tool-call cap of the agent-loop namespace|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-general`<br>`@deepseek-ai/dsh-client-ui-settings-general`|Settings ownerless-copy and product onboarding plugin: the General section, shell trigger/header chrome content, settings dictionaries, and the versioned welcome notice|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-models`<br>`@deepseek-ai/dsh-client-ui-settings-models`|Models settings and shared product-onboarding dialogs over existing settings and credential joins|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-plugin-inventory`<br>`@deepseek-ai/dsh-client-ui-settings-plugin-inventory`|Read-only Cordis Loader inventory tab in Web Plugins settings|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-plugins`<br>`@deepseek-ai/dsh-client-ui-settings-plugins`|Built-in plugins settings section for the dsh web client: the Settings navigation entry and the tab chrome feature-owned tabs register into|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-session-log`<br>`@deepseek-ai/dsh-client-ui-settings-session-log`|General settings control for Session-log upload with DeepSeek API requests|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-shell`<br>`@deepseek-ai/dsh-client-ui-settings-shell`|Settings page of the shell executor on the dsh web client's Plugins page: the command timeout and the per-stream output cap of the shell namespace|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-subagent`<br>`@deepseek-ai/dsh-client-ui-settings-subagent`|Settings page of Subagent delegation on the dsh web client's Plugins page: recursion depth, parallel capacity, and the models agents may choose for subagents|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-settings-web-search`<br>`@deepseek-ai/dsh-client-ui-settings-web-search`|Settings page of the DeepSeek web-search provider on the dsh web client's Plugins page: its API key, endpoint, and per-request search budget|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-shortcuts`<br>`@deepseek-ai/dsh-client-ui-shortcuts`|Keyboard shortcut reference, recording, and local preference editing|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-sidebar`<br>`@deepseek-ai/dsh-client-ui-sidebar`|Sidebar plugin: session multi-level tree, search, grouping, state dots|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-sidebar-browser`<br>`@deepseek-ai/dsh-client-ui-sidebar-browser`|Sandboxed Web browser tabs for the right Sidebar|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-sidebar-documentpreview`<br>`@deepseek-ai/dsh-client-ui-sidebar-documentpreview`|Extensible Sidebar previews for Office documents, spreadsheets, Markdown, code, images, PDF, HTML, and plain text|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-sidebar-files`<br>`@deepseek-ai/dsh-client-ui-sidebar-files`|Workspace file tree tab type for the right Sidebar: lazy directory listing over the workspaceFiles Remote namespace, opening files into the Sidebar|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-sidebar-right`<br>`@deepseek-ai/dsh-client-ui-sidebar-right`|Right Sidebar: the docking surface's session-bound state, its panel and header expand control, and the navigation service over it|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-sidebar-terminal`<br>`@deepseek-ai/dsh-client-ui-sidebar-terminal`|Interactive shell tabs for the right Sidebar|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-skill`<br>`@deepseek-ai/dsh-client-ui-skill`|Web skill references and the dedicated skill tool row|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-slots`<br>`@deepseek-ai/dsh-client-ui-slots`|Slot registry pure core: typed ordinary Slots and reusable Component Factories, derived props, Store seats, and renderer installation|`src/index.ts`|实现／接口选读|未独立运行|1/3|已选读接口的其余实现未全审|
|`packages/client/ui-subagent`<br>`@deepseek-ai/dsh-client-ui-subagent`|Subagent conversation catalog, continuation routing UI, and '@' reference source|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-theme`<br>`@deepseek-ai/dsh-client-ui-theme`|Theme plugin: Host bootstrap for the pre-plugin palette; DOM-free ThemeRuntime for light/dark/system state; --dsw-* token styles and Appearance settings row|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-tool`<br>`@deepseek-ai/dsh-client-ui-tool`|Client Tool call-tree renderer and keyed per-tool presentation slot|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-trajectory`<br>`@deepseek-ai/dsh-client-ui-trajectory`|Trajectory event ledger with an interactive timing overview: pure-consumer plugin registering into the conversation ViewMap (no service)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-user-questions`<br>`@deepseek-ai/dsh-client-ui-user-questions`|Web ask_user_question composer takeover and plan-review presentation UI|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-workflow-run`<br>`@deepseek-ai/dsh-client-ui-workflow-run`|Durable workflow-run Conversation Node and nested member disclosure for dsh web|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/ui-workspace`<br>`@deepseek-ai/dsh-client-ui-workspace`|Workspace picker plugin: one WorkspacePicker registered into the sidebar and empty-state workspace slots|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/client/web`<br>`@deepseek-ai/dsh-client-web`|Web boot kernel: static module table, Cordis loader, framework-free boot page, and UI-renderer handoff|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/compaction/command-compact`<br>`@deepseek-ai/dsh-command-compact`|Human-facing slash command for explicit session compaction|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/compaction/compaction`<br>`@deepseek-ai/dsh-compaction`|Abstract compaction service seam (ctx.compaction) for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/compaction/compaction-basic`<br>`@deepseek-ai/dsh-compaction-basic`|Token-meter-driven compaction policy and LLM summarization backend for the DeepSeek Harness|`src/index.ts`<br>`src/region.ts`<br>`src/summarizer.ts`<br>`tests/compaction-basic.spec.ts`|关键实现深读（选段）|V10：对应选定测试文件通过；非整包／完整应用验证|1/3/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/compaction/compaction-image-offload`<br>`@deepseek-ai/dsh-compaction-image-offload`|Durable image offload for image-capable routes: replace over-budget request images with placeholders and retry|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/compaction/compaction-tool-result-pruner`<br>`@deepseek-ai/dsh-compaction-tool-result-pruner`|Replay-safe model-free head/middle/tail pruning for tool-result surface nodes|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/computer-use/computer-use`<br>`@deepseek-ai/dsh-computer-use`|Exclusive named computer-use provider registration|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/context/agent-instructions`<br>`@deepseek-ai/dsh-agent-instructions`|Workspace context loader for AGENTS.md/CLAUDE.md instruction files|`src/index.ts`|关键实现深读（选段）|未独立运行|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/context/file-reference`<br>`@deepseek-ai/dsh-file-reference`|File-reference discovery contract and shared @file grammar|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/context/file-reference-local`<br>`@deepseek-ai/dsh-file-reference-local`|Local-filesystem ctx.fileReferences provider with bounded fuzzy indexes|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/context/session-reference`<br>`@deepseek-ai/dsh-session-reference`|Cross-session snapshot references and durable untrusted model context (ctx.sessionReferenceResolver)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/context/time-context`<br>`@deepseek-ai/dsh-time-context`|Durable per-step context with the current time and elapsed time|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/context/tmux-context`<br>`@deepseek-ai/dsh-tmux-context`|Opt-in durable per-step context with this agent's tmux pane and window location|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/core/agent`<br>`@deepseek-ai/dsh-agent`|Agent interface, registry, initiator scope, and event vocabulary for the DeepSeek Harness|`src/index.ts`|关键实现深读（选段）|未独立运行|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/core/agent-default-model`<br>`@deepseek-ai/dsh-agent-default-model`|Default model selection shared by Agent entry points|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/core/agent-loop`<br>`@deepseek-ai/dsh-agent-loop`|The concrete agent loop plugin for the DeepSeek Harness|`src/agent.ts`<br>`src/assistant-stream.ts`<br>`src/inbox.ts`<br>`src/index.ts`<br>`src/runtime-context.ts`<br>`src/tool-calls.ts`<br>`tests/loop.spec.ts`<br>`tests/mock-adapter.ts`|关键实现深读（选段）|V01/V04/V05|1/2/3/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/core/agent-tool-presentation`<br>`@deepseek-ai/dsh-agent-tool-presentation`|Agent-plane presentation selector: composes one agent's tools as PTC mode, native, or both|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/core/scope`<br>`@deepseek-ai/dsh-scope`|Scoped-context registration primitive (scope tags, scope-filtered event dispatch) for the DeepSeek Harness|`src/index.ts`|关键实现深读（选段）|未独立运行|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/core/session`<br>`@deepseek-ai/dsh-session`|Event-sourced session store for the DeepSeek Harness|`src/index.ts`|关键实现深读（选段）|V01/V04|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/core/system-prompt`<br>`@deepseek-ai/dsh-system-prompt`|System prompt assembly registry for the DeepSeek Harness|`src/index.ts`|关键实现深读（选段）|未独立运行|1/2/3|目标部署／真实provider与完整suite未验证|
|`packages/core/tools`<br>`@deepseek-ai/dsh-tools`|Tool registry and execution pipeline for the DeepSeek Harness|`src/index.ts`<br>`src/schema.ts`<br>`src/types.ts`|关键实现深读（选段）|V01/V05消费者验证|1/2/3/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/credentials/authorization`<br>`@deepseek-ai/dsh-authorization`|Authorization seam (ctx.authorization): plugin-owned flows that obtain a credential through a conversation with the human|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/credentials/credentials`<br>`@deepseek-ai/dsh-credentials`|Abstract credential seam (ctx.credentials): settings carry references to secrets, providers own the values|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/credentials/credentials-local`<br>`@deepseek-ai/dsh-credentials-local`|File-backed credentials provider ($DSH_HOME/.env under the live process environment) for the DeepSeek Harness|`src/index.ts`|实现／接口选读|未独立运行|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/credentials/deepseek-account`<br>`@deepseek-ai/dsh-deepseek-account`|Read account state and resolve official API credentials|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/credentials/deepseek-account-platform`<br>`@deepseek-ai/dsh-deepseek-account-platform`|Authorize DeepSeek accounts through browser PKCE|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/deliverables/tool-present`<br>`@deepseek-ai/dsh-tool-present`|Explicit workspace file delivery declarations for the DeepSeek Harness|`src/index.ts`|关键实现深读（选段）|V08：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/deliverables/workspace-changes`<br>`@deepseek-ai/dsh-workspace-changes`|Per-turn workspace file changes recorded from git working-tree snapshots and whole-file captures, with per-file comparisons, for the DeepSeek Harness|`README.md`<br>`src/index.ts`<br>`src/recorder.ts`<br>`tests/plugin.spec.ts`|关键实现深读（选段）|V10：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/document/office-to-pdf`<br>`@deepseek-ai/dsh-office-to-pdf`|Shared Office-to-PDF conversion with bounded queues and caching|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/agent-team`<br>`@deepseek-ai/dsh-experimental-agent-team`|Implicit-root Agent Teams roster, durable peer mailbox, and shared task DAG|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/agent-team-profile`<br>`@deepseek-ai/dsh-experimental-agent-team-profile`|Agent Teams collaboration, tools, and Web UI in one experimental bundle|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/api-speech-to-text`<br>`@deepseek-ai/dsh-experimental-api-speech-to-text`|Authenticated experimental speech transcription for browser clients|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/auto-review`<br>`@deepseek-ai/dsh-experimental-auto-review`|Per-tool LLM authorization review for the DeepSeek Harness Auto permission preset|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/browser-use-chrome-devtools-mcp`<br>`@deepseek-ai/dsh-experimental-browser-use-chrome-devtools-mcp`|Experimental per-Session Chromium browser tools through chrome-devtools-mcp|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/browser-use-playwright-mcp`<br>`@deepseek-ai/dsh-experimental-browser-use-playwright-mcp`|Experimental per-Session Chromium browser tools through @playwright/mcp|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/browser-use-runtime`<br>`@deepseek-ai/dsh-experimental-browser-use-runtime`|Session-owned browser resource lifecycles and MCP integration for experimental providers|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/browser-use-stagehand-native`<br>`@deepseek-ai/dsh-experimental-browser-use-stagehand-native`|Experimental Stagehand browser tools with separately configured native models|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/claude-code-mods`<br>`@deepseek-ai/dsh-experimental-claude-code-mods`|Experimental bridge: load Claude Code mods (hooks modules) and run their hook chains on DeepSeek Harness extension points|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/client-ui-agent-team`<br>`@deepseek-ai/dsh-experimental-client-ui-agent-team`|Web Agent Teams roster, task board, and teammate navigation|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/client-ui-claude-code-mods`<br>`@deepseek-ai/dsh-experimental-client-ui-claude-code-mods`|Web band above the prompt for Claude Code mods: draws each session's mod tree and sends button presses back to the bridge|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/client-ui-voice-input`<br>`@deepseek-ai/dsh-experimental-client-ui-voice-input`|Record speech and insert editable text into the conversation draft|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/computer-use-cua-driver-mcp`<br>`@deepseek-ai/dsh-experimental-computer-use-cua-driver-mcp`|Experimental computer use through an installed Cua Driver MCP executable|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/computer-use-cua-driver-native`<br>`@deepseek-ai/dsh-experimental-computer-use-cua-driver-native`|Experimental computer-use provider embedding the Cua Driver native npm SDK|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/inspector`<br>`@deepseek-ai/dsh-experimental-inspector`|Experimental cross-realm CDP hub for Host debugging and Client Runtime inspection|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/inspector-profile`<br>`@deepseek-ai/dsh-experimental-inspector-profile`|Optional Web bundle for raw Session logs and Chat node inspection|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/ptc-runtime-python`<br>`@deepseek-ai/dsh-experimental-ptc-runtime-python`|CPython subprocess implementation of the DeepSeek Harness PTC execution seam|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/session-inspector`<br>`@deepseek-ai/dsh-experimental-session-inspector`|Experimental virtualized Session log and live Chat group/node inspectors|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/speech-to-text`<br>`@deepseek-ai/dsh-experimental-speech-to-text`|Experimental speech recognition with independently selectable providers|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/speech-to-text-sensevoice`<br>`@deepseek-ai/dsh-experimental-speech-to-text-sensevoice`|Local SenseVoice ONNX transcription with a managed sherpa-onnx process|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/tool-agent-team`<br>`@deepseek-ai/dsh-experimental-tool-agent-team`|Scoped model-facing Agent Teams tools over ctx.agentTeams|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/voice-input-bundle`<br>`@deepseek-ai/dsh-experimental-voice-input-bundle`|Experimental voice input with local SenseVoice; downloads its runtime on first use|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/webworker-packer`<br>`@deepseek-ai/dsh-experimental-webworker-packer`|Build-time packer for the browser runtime's base VFS image and ordered data-overlay archives|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/experimental/webworker-runtime`<br>`@deepseek-ai/dsh-experimental-webworker-runtime`|Browser-only harness runtime: in-memory VFS, module transform and loader, postMessage tunnel, and the dedicated Web Worker assembly, with the Node-compatibility layer that lets the host tree run unchanged|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/extensions/cordis-client-runner`<br>`@deepseek-ai/dsh-cordis-client-runner`|Browser half of dynamic dual-half plugin packages: event subscription, closure evaluation, guard facade, and loader entries|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/extensions/cordis-host-runner`<br>`@deepseek-ai/dsh-cordis-host-runner`|Dynamic package definition registry, host-half sandbox lifecycle, and invoke handler table for model-mounted dual-half packages|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/extensions/tool-cordis`<br>`@deepseek-ai/dsh-tool-cordis`|Read-only runtime API inspection for Harness plugin development|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/extensions/ui-cordis`<br>`@deepseek-ai/dsh-client-ui-cordis`|Cordis dynamic-plugin definition card: the keyed cordis_define tool row with its run/stop switch|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/feedback/command-feedback`<br>`@deepseek-ai/dsh-command-feedback`|Log-only session feedback: the record event, the sessionFeedback Host Remote, and the human-facing slash command|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/feedback/message-feedback`<br>`@deepseek-ai/dsh-message-feedback`|Canonical Session-log ratings and notes for finalized assistant messages|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/fs/fs`<br>`@deepseek-ai/dsh-fs`|Abstract filesystem capability seam (ctx.fs) for the DeepSeek Harness — vocabulary types, the FileSystem service (text IO + optional version-guarded atomic mutations), and the fs/* policy event vocabulary|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/fs/fs-local`<br>`@deepseek-ai/dsh-fs-local`|Local-filesystem implementation of the DeepSeek Harness filesystem seam (ctx.fs)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/fs/fs-observation-policy`<br>`@deepseek-ai/dsh-fs-observation-policy`|File-context policy plugin for the DeepSeek Harness — observed-state, read-before-edit, and version-guarded write/edit added over the ctx.fs provider seam through the fs/* event gate (no service API)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/fs/fs-sandbox`<br>`@deepseek-ai/dsh-fs-sandbox`|Sandbox-enforcing implementation of the DeepSeek Harness filesystem seam: fences write/edit by the per-call sandbox mode (read-only denies mutation, workspace-write contains it to the workspace + temp roots) while reads pass through|`src/index.ts`|实现／接口选读|未独立运行|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/fs/tool-fs`<br>`@deepseek-ai/dsh-tool-fs`|Model-facing filesystem tools (read, write, edit) over the DeepSeek Harness filesystem seam (ctx.fs)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/fs/tool-fs-search`<br>`@deepseek-ai/dsh-tool-fs-search`|Model-facing filesystem discovery tools (glob, grep) backed by the packaged ripgrep binary (@vscode/ripgrep)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/fs/tool-str-replace-editor`<br>`@deepseek-ai/dsh-tool-str-replace-editor`|Model-facing view, create, literal replace, and line insert tool over the Harness filesystem service|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/goal/command-goal`<br>`@deepseek-ai/dsh-command-goal`|Human-facing slash command for persisted same-session goals|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/goal/goal`<br>`@deepseek-ai/dsh-goal`|Event-sourced same-session goal state and lifecycle service for the DeepSeek Harness|`README.md`<br>`src/fold.ts`<br>`src/index.ts`|关键实现深读（选段）|V08：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/goal/goal-round-driver`<br>`@deepseek-ai/dsh-goal-round-driver`|Race-fenced same-session goal-round driver|`src/index.ts`|关键实现深读（选段）|V08：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/goal/tool-goal`<br>`@deepseek-ai/dsh-tool-goal`|Model-facing same-session goal tools with execution-time authority checks|`src/authority.ts`<br>`src/index.ts`|关键实现深读（选段）|V08：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/guard/repeat-tool-reminder`<br>`@deepseek-ai/dsh-repeat-tool-reminder`|Repeat-tool-call guard plugin: advisory reminders when an agent loops on identical tool calls|`src/index.ts`|关键实现深读（选段）|未独立运行|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/guard/timeout-policy`<br>`@deepseek-ai/dsh-tool-call-timeout-policy`|Tool-call timeout policy: a tools/execute wrapper that arms a per-tool deadline on exec.signal and returns TOOL_TIMEOUT when it wins|`src/index.ts`|实现／接口选读|V03|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/hooks/hook-protocol`<br>`@deepseek-ai/dsh-hook-protocol`|Shared Claude Code / Codex hook wire protocol: matcher engine, stdin/exit-code/stdout codec, multi-hook merge, and hook/* session events|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/hooks/hooks-claude-code`<br>`@deepseek-ai/dsh-hooks-claude-code`|Bridge plugin: run a Claude Code hooks.json / settings hook config on the DeepSeek Harness interception seams|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/hooks/hooks-codex`<br>`@deepseek-ai/dsh-hooks-codex`|Bridge plugin: run a Codex hooks.json hook config on the DeepSeek Harness interception seams|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/directory-picker`<br>`@deepseek-ai/dsh-host-directory-picker`|Abstract workspace-directory picking seam (ctx.directoryPicker) for the DeepSeek Harness web GUI host|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/directory-picker-auto`<br>`@deepseek-ai/dsh-host-directory-picker-auto`|Adaptive chooser of the directory-picker seam: resolves the host situation at boot and mounts the native or browse backend for the DeepSeek Harness web GUI host|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/directory-picker-browse`<br>`@deepseek-ai/dsh-host-directory-picker-browse`|In-app browsing backend of the directory-picker seam (listing/creation primitives over the host filesystem)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/directory-picker-native`<br>`@deepseek-ai/dsh-host-directory-picker-native`|Native-OS-chooser backend of the directory-picker seam for the DeepSeek Harness web GUI host|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/frontend-static`<br>`@deepseek-ai/dsh-host-frontend-static`|SPA dist server for the Web shell: owns the webserver fallback seat, serving explicit index entries and static assets with traversal rejection and 404 misses|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/open-in-app`<br>`@deepseek-ai/dsh-host-open-in-app`|Host half of open-in-app: resolved application catalog, icons, and the launch endpoint as three webServer routes|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/plugin-inventory`<br>`@deepseek-ai/dsh-host-plugin-inventory`|Read-only Remote projection of current Cordis Loader plugin state|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/product-telemetry-otel`<br>`@deepseek-ai/dsh-host-product-telemetry-otel`|Explicit product usage events exported through OpenTelemetry HTTP logs|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/host/webserver`<br>`@deepseek-ai/dsh-host-webserver`|Web route-registration plugin: HTTP and upgrade routes, index transform taps, and static dist fallback; knows no harness concepts|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/identity/anonymous-user-id`<br>`@deepseek-ai/dsh-anonymous-user-id`|Shared anonymous user identity for DeepSeek Harness telemetry and feedback correlation|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/interaction/commands`<br>`@deepseek-ai/dsh-commands`|Plugin-owned human command registry for DeepSeek Harness UIs|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/interaction/permission-presets`<br>`@deepseek-ai/dsh-permission-presets`|User-facing permission presets (ctx.permissionPresets) for the DeepSeek Harness: one product-level Permissions select bundling the sandbox-mode and approval-policy knobs, written through to their own session events|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/interaction/tool-ask-user`<br>`@deepseek-ai/dsh-tool-ask-user`|Model-facing ask_user_question tool over the ctx.userQuestions seam|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/interaction/user-approval`<br>`@deepseek-ai/dsh-user-approval`|User-approval seam (ctx.approval) for the DeepSeek Harness: one-shot permission decisions dispatched to composed answerers over the approval/request waterfall, fail-closed by default|`src/index.ts`|实现／接口选读|V02|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/interaction/user-questions`<br>`@deepseek-ai/dsh-user-questions`|Abstract user-questions seam (ctx.userQuestions) for asking the human during agent runs|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/jobs/jobs`<br>`@deepseek-ai/dsh-jobs`|Background job registry (ctx.jobs) for the DeepSeek Harness — shared ids, owner isolation, polling, cancellation, and completion listeners for long-running tool work|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/jobs/jobs-local`<br>`@deepseek-ai/dsh-jobs-local`|Process-local implementation of the DeepSeek Harness background job registry seam|`src/index.ts`<br>`tests/jobs.spec.ts`|关键实现深读（选段）|V10：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/jobs/tool-jobs`<br>`@deepseek-ai/dsh-tool-jobs`|Model-facing background job control tools (job_output, job_list, job_kill) over the ctx.jobs registry|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/llm/deepseek-llm-api-extensions`<br>`@deepseek-ai/dsh-deepseek-llm-api-extensions`|Additive request-field registry for the official DeepSeek LLM API adapter|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/llm/llm`<br>`@deepseek-ai/dsh-llm`|Provider-neutral LLM service interface for the DeepSeek Harness|`src/index.ts`<br>`src/types.ts`|关键实现深读（选段）|V01/V05消费者验证|1/2/3/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/llm/llm-deepseek`<br>`@deepseek-ai/dsh-llm-deepseek`|DeepSeek Messages adapter|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/llm/llm-deepseek-account`<br>`@deepseek-ai/dsh-llm-deepseek-account`|DeepSeek account provider authentication and discovery|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/llm/llm-deepseek-api-key`<br>`@deepseek-ai/dsh-llm-deepseek-api-key`|DeepSeek api-key provider authentication and discovery|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/llm/llm-pi-ai`<br>`@deepseek-ai/dsh-llm-pi-ai`|pi-ai-backed DeepSeek adapter for the DeepSeek Harness LLM seam (design-verification twin of dsh-llm-deepseek)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/llm/llm-retry`<br>`@deepseek-ai/dsh-llm-retry`|Provider-routed LLM request retry policy for the DeepSeek Harness|`src/index.ts`|关键实现深读（选段）|V02|1/2/3/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/llm/plugin-package-inventory-deepseek`<br>`@deepseek-ai/dsh-plugin-package-inventory-deepseek`|Active Loader-backed plugin package inventory for official DeepSeek LLM API requests|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/llm/token-meter`<br>`@deepseek-ai/dsh-token-meter`|Replay-aware token measurement service (ctx.tokenMeter) for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/lsp/lsp`<br>`@deepseek-ai/dsh-lsp`|Abstract LSP capability seam (ctx.lsp) for the DeepSeek Harness — language-server provider registry keyed by branded id and extension mapping, order-independent per-query selection, normalized definition/references/implementation/hover requests and results, and the LspError taxonomy|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/lsp/lsp-stdio`<br>`@deepseek-ai/dsh-lsp-stdio`|Generic stdio language-server provider for the DeepSeek Harness LSP capability seam (ctx.lsp) — spawns configured servers, translates JSON-RPC, and serves transient-open goToDefinition/findReferences/goToImplementation/hover queries in the host filesystem namespace|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/lsp/tool-lsp`<br>`@deepseek-ai/dsh-tool-lsp`|Model-facing lsp tool over the DeepSeek Harness LSP capability seam (ctx.lsp) — one read-only tool with goToDefinition/findReferences/goToImplementation/hover operations, one-based UTF-16 cursor coordinates, bounded location rendering, and hover normalization|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/mcp/mcp-client`<br>`@deepseek-ai/dsh-mcp-client`|MCP client bridge: connects to MCP servers and registers their tools on ctx.tools|`src/server-context.ts`<br>`src/tools.ts`|关键实现深读（选段）|未独立运行|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/mcp/mcp-resources`<br>`@deepseek-ai/dsh-mcp-resources`|Scoped MCP resource discovery and reading through shared model tools|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/plan/plan-mode`<br>`@deepseek-ai/dsh-plan-mode`|Logged per-agent plan mode with deployment guidance, a direct slash command, and a user-reviewed exit|`src/index.ts`<br>`tests/plan-mode.spec.ts`|关键实现深读（选段）|V10：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/preset/agent-preset`<br>`@deepseek-ai/dsh-agent-preset`|Declare an Agent capability composition in Cordis YAML|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/preset/agent-preset-registry`<br>`@deepseek-ai/dsh-agent-preset-registry`|Declarative Agent preset registry and profile-backed editing|`src/index.ts`|实现／接口选读|未独立运行|1/3|已选读接口的其余实现未全审|
|`packages/preset/persona`<br>`@deepseek-ai/dsh-persona`|Composition-authored deployment persona section for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/ptc-runtime/ptc-runtime`<br>`@deepseek-ai/dsh-ptc-runtime`|Abstract PTC execution seam (ctx.ptcRuntime) for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/ptc-runtime/ptc-runtime-node`<br>`@deepseek-ai/dsh-ptc-runtime-node`|Sandboxed Node process implementation of the DeepSeek Harness PTC execution capability|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/sandbox/sandbox`<br>`@deepseek-ai/dsh-sandbox`|Abstract process-sandbox seam (ctx.sandbox) for the DeepSeek Harness: same-world confinement vocabulary and the SandboxProvider contract|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/sandbox/sandbox-local`<br>`@deepseek-ai/dsh-sandbox-local`|Local process-sandbox backends for the DeepSeek Harness sandbox seam: bwrap, the npm-distributed landlock-run launcher, macOS Seatbelt, or the Windows ACL restricted-token runner — functionally probed, fail-closed|`src/index.ts`|实现／接口选读|未独立运行|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/sandbox/sandbox-policy`<br>`@deepseek-ai/dsh-sandbox-policy`|Per-call sandbox policy resolver and current model context: deployment fallbacks plus each session's mode and workspace root, shared by every enforcing capability family|`src/index.ts`|实现／接口选读|未独立运行|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/sandbox/sandbox-windows-acl`<br>`@deepseek-ai/dsh-sandbox-windows-acl`|Windows ACL write-restriction sandbox backend (restricted-token spawn with capability-SID write allowlist) for the DeepSeek Harness sandbox seam|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/schedule/schedule`<br>`@deepseek-ai/dsh-schedule`|Host-wide durable reminders with shared management and original-Session delivery|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/schedule/tool-schedule`<br>`@deepseek-ai/dsh-tool-schedule`|Model-facing reminder management tools (schedule_create, schedule_list, schedule_update, schedule_delete) over the Host ctx.schedule service|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/sdk/client`<br>`@deepseek-ai/dsh-sdk-client`|TypeScript client SDK for driving a DeepSeek Harness runtime subprocess over stdio JSON-RPC: the DeepSeekHarness high-level turns API and the lower-level HarnessClient|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/sdk/protocol`<br>`@deepseek-ai/dsh-sdk-protocol`|Shared wire protocol for the DeepSeek Harness SDK runtime: the newline-delimited JSON-RPC stdio transport and the named request, result, and notification types spoken between the runtime server and SDK clients|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/sdk/server`<br>`@deepseek-ai/dsh-sdk-jsonrpc-server`|Stdio JSON-RPC server plugin for out-of-process DeepSeek Harness SDK clients|`src/index.ts`<br>`src/server.ts`|关键实现深读（选段）|V03|1/3/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/session-query/session-log-export`<br>`@deepseek-ai/dsh-session-log-export`|Web Session-log export command and shared download dialog|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）/专栏（对应机制）|实现与运行行为未深核|
|`packages/session-query/session-query`<br>`@deepseek-ai/dsh-session-query`|Combined session query service contract with concrete reads, traces, and filters|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session-query/session-query-sqlite`<br>`@deepseek-ai/dsh-session-query-sqlite`|Concrete ctx.sessionQuery backend with SQLite FTS5 search|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session-query/tool-session-query`<br>`@deepseek-ai/dsh-tool-session-query`|Workspace-authorized model-facing session history search, trace, and event read tools|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-checkpoint-policy`<br>`@deepseek-ai/dsh-session-checkpoint-policy`|Semantic session durability checkpoints before model requests and tool side effects|`src/index.ts`|关键实现深读（选段）|未独立运行|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/session/session-format`<br>`@deepseek-ai/dsh-session-format`|Streaming adjacent Session format migration machinery|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-format-catalog`<br>`@deepseek-ai/dsh-session-format-catalog`|Build-static first-party Session format codec and migration catalog|`src/index.ts`|实现／接口选读|未独立运行|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/session/session-format-v0-to-v1`<br>`@deepseek-ai/dsh-session-format-v0-to-v1`|Frozen released-v0 Session codec and identity migration to v1|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-format-v1-to-v2`<br>`@deepseek-ai/dsh-session-format-v1-to-v2`|Frozen released-v1 Session codec and assistant-stream migration to v2|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-format-v2-to-v3`<br>`@deepseek-ai/dsh-session-format-v2-to-v3`|Streaming system-prompt, canonical-envelope and PTC migration into V3|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-format-v3-to-v4`<br>`@deepseek-ai/dsh-session-format-v3-to-v4`|Streaming tool-role migration and delivery validation from Session V3 to V4|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-log-deepseek`<br>`@deepseek-ai/dsh-session-log-deepseek`|Incremental lossless session-log request extension for the official DeepSeek LLM API|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-persistence`<br>`@deepseek-ai/dsh-session-persistence`|Abstract durable session persistence seam (ctx.sessionPersistence) for the DeepSeek Harness|`src/index.ts`|关键实现深读（选段）|未独立运行|1/2/3|目标部署／真实provider与完整suite未验证|
|`packages/session/session-persistence-jsonl`<br>`@deepseek-ai/dsh-session-persistence-jsonl`|JSONL durable session persistence backend for the DeepSeek Harness|`src/index.ts；src/storage.ts；src/lease.ts`|关键实现深读（选段）|V03|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/session/session-projection`<br>`@deepseek-ai/dsh-session-projection`|Session-projection seam: the merge-extensible projection type table, the provider contract, and the ctx.sessionProjections registry serving whole current values of log-derived per-session state|`src/index.ts`|关键实现深读（选段）|V02|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`packages/session/session-projection-cache`<br>`@deepseek-ai/dsh-session-projection-cache`|Persisted projection cache (ctx.sessionProjectionCache): durable per-session checkpoint records on the session_projcache storage domain (per-record layout), throttled write-behind, and the cached listing read|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-stats`<br>`@deepseek-ai/dsh-session-stats`|Whole-log conversation counts and wall times projection (sessionStats) for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-telemetry`<br>`@deepseek-ai/dsh-session-telemetry`|SessionTelemetryBackend seam for the DeepSeek Harness: session-event capture, projection, redaction, and handoff to a reporting backend|`src/coordinator.ts`|关键实现深读（选段）|V08：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/session/session-telemetry-otel`<br>`@deepseek-ai/dsh-session-telemetry-otel`|Feedback-authorized Session logs over byte-bounded OpenTelemetry HTTP requests|`README.md`<br>`src/index.ts`|关键实现深读（选段）|V08：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/session/session-title`<br>`@deepseek-ai/dsh-session-title`|Log-backed session title service and provider registry for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-title-all-prompts-llm`<br>`@deepseek-ai/dsh-session-title-all-prompts-llm`|All-user-messages LLM provider plugin for DeepSeek Harness session titles|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-title-first-prompt-llm`<br>`@deepseek-ai/dsh-session-title-first-prompt-llm`|First-message LLM provider plugin for DeepSeek Harness session titles|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-title-llm`<br>`@deepseek-ai/dsh-session-title-llm`|Shared LLM generation policy for DeepSeek Harness session-title providers|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/session/session-turn-outline`<br>`@deepseek-ai/dsh-session-turn-outline`|Whole-log turn outline projection (turnOutline) for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/settings/settings`<br>`@deepseek-ai/dsh-settings`|Abstract user-settings seam (ctx.settings) for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/bash-local`<br>`@deepseek-ai/dsh-bash-local`|Local-subprocess implementation of the DeepSeek Harness bash executor seam|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/bash-sandbox`<br>`@deepseek-ai/dsh-bash-sandbox`|Sandbox-consuming implementation of the DeepSeek Harness bash executor seam (confines every command via ctx.sandbox, reports denial/enforcement result facts)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/pwsh-local`<br>`@deepseek-ai/dsh-pwsh-local`|Local PowerShell implementation of the DeepSeek Harness bash executor seam|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/pwsh-sandbox`<br>`@deepseek-ai/dsh-pwsh-sandbox`|Sandbox-consuming implementation of the DeepSeek Harness PowerShell executor seam (confines every command via ctx.sandbox, reports denial/enforcement result facts)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/shell`<br>`@deepseek-ai/dsh-shell`|Abstract bash executor seam (ctx.shell) for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/shell-env`<br>`@deepseek-ai/dsh-shell-env`|Tool-independent managed DSH_* shell environment registry|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/tool-bash`<br>`@deepseek-ai/dsh-tool-bash`|Model-facing bash tool with optional generic background-job and sandbox-escalation support|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/tool-bash-persistent`<br>`@deepseek-ai/dsh-tool-bash-persistent`|Model-facing owner-scoped persistent Bash tool backed by the Harness PTY service|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/tool-pwsh`<br>`@deepseek-ai/dsh-tool-pwsh`|Model-facing pwsh tool over the bash executor seam|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/shell/tool-pwsh-persistent`<br>`@deepseek-ai/dsh-tool-pwsh-persistent`|Model-facing owner-scoped persistent PowerShell tool backed by the Harness PTY service|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/skill/skill`<br>`@deepseek-ai/dsh-skill`|Agent skill provider registry for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/skill/skill-badge`<br>`@deepseek-ai/dsh-skill-badge`|Bundled dsh badge skill provider for DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/skill/skill-filesystem`<br>`@deepseek-ai/dsh-skill-filesystem`|Local filesystem skill provider for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/skill/skill-office`<br>`@deepseek-ai/dsh-skill-office`|Bundled Word, PowerPoint, and Excel workflows and structural checks|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/skill/tool-skill`<br>`@deepseek-ai/dsh-tool-skill`|Model-facing skill loading tool for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/skill/tool-workspace-dependencies`<br>`@deepseek-ai/dsh-tool-workspace-dependencies`|The load_workspace_dependencies tool: absolute paths into a bundled Python, Node.js, and pnpm payload|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/spill/spill`<br>`@deepseek-ai/dsh-spill`|Abstract spill storage seam (ctx.spillStore) for the DeepSeek Harness — save oversized tool text and return a retrieval locator|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/spill/spill-local`<br>`@deepseek-ai/dsh-spill-local`|Local-filesystem implementation of the DeepSeek Harness spill storage seam (private session-scoped files)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/spill/spill-policy`<br>`@deepseek-ai/dsh-spill-policy`|Token-budgeted tool-result retention with recoverable text and image paths|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/ssh/fs-ssh`<br>`@deepseek-ai/dsh-fs-ssh`|Filesystem provider over the shared POSIX SSH helper|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/ssh/sandbox-ssh`<br>`@deepseek-ai/dsh-sandbox-ssh`|Remote POSIX sandbox argv provider over the shared SSH helper|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/ssh/ssh`<br>`@deepseek-ai/dsh-ssh`|Shared OpenSSH connection and versioned POSIX remote helper|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/ssh/subprocess-ssh`<br>`@deepseek-ai/dsh-subprocess-ssh`|Subprocess and terminal provider over the shared POSIX SSH helper|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/storage/storage`<br>`@deepseek-ai/dsh-storage`|Storage hub (ctx.storage): named backend registry plus mounted data-form facilities for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/storage/storage-domain`<br>`@deepseek-ai/dsh-storage-domain`|Domain data form (ctx.storage.domain): schema-validated, event-emitting KV domains over storage backends for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/storage/storage-json`<br>`@deepseek-ai/dsh-storage-json`|JSON file KV storage backend for the DeepSeek Harness storage hub|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/storage/storage-sqlite`<br>`@deepseek-ai/dsh-storage-sqlite`|SQLite storage backend (kv facet) for the DeepSeek Harness storage hub|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subagent/subagent`<br>`@deepseek-ai/dsh-subagent`|Abstract subagent seam (ctx.subagents): named-provider registry for delegating to child agents|`src/index.ts`|关键实现深读（选段）|未独立运行|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/subagent/subagent-acp`<br>`@deepseek-ai/dsh-subagent-acp`|Out-of-process ACP subagent backend: drives a child agent in a spawned subprocess over the Agent Client Protocol|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subagent/subagent-claude-code`<br>`@deepseek-ai/dsh-subagent-claude-code`|One-shot Claude Code subagent provider over the official Agent SDK|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subagent/subagent-codex`<br>`@deepseek-ai/dsh-subagent-codex`|One-shot Codex subagent provider over the official app-server protocol|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subagent/subagent-dsh-sdk`<br>`@deepseek-ai/dsh-subagent-dsh-sdk`|Out-of-process SDK subagent backend: drives a child DeepSeek Harness runtime subprocess over stdio JSON-RPC through the TypeScript SDK client|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subagent/subagent-fork-in-process`<br>`@deepseek-ai/dsh-subagent-fork-in-process`|In-process fork subagent backend: runs a child agent seeded with a prefix of the parent's log|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subagent/subagent-in-process-driver`<br>`@deepseek-ai/dsh-subagent-in-process-driver`|Shared in-process subagent run driver: drives a child agent on ctx.agents (used by the spawn and fork backends)|`src/index.ts`<br>`src/structured.ts`<br>`tests/structured.spec.ts`|关键实现深读（选段）|V10：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/subagent/subagent-spawn-in-process`<br>`@deepseek-ai/dsh-subagent-spawn-in-process`|In-process spawn subagent backend: runs a fresh child agent on ctx.agents|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subagent/tool-subagent`<br>`@deepseek-ai/dsh-tool-subagent`|Model-facing subagent delegation tool over the ctx.subagents seam|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subagent/tool-subagent-control`<br>`@deepseek-ai/dsh-tool-subagent-control`|Globally named send_message, interrupt_agent, and list_agents tools over ctx.subagents continuations|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subprocess/subprocess`<br>`@deepseek-ai/dsh-subprocess`|Subprocess seam (ctx.subprocess) for the DeepSeek Harness — managed process groups, bounded spill-backed output, and escalated kills behind one abstract service|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/subprocess/subprocess-local`<br>`@deepseek-ai/dsh-subprocess-local`|Local-subprocess implementation of the DeepSeek Harness subprocess seam|`src/index.ts`|实现／接口选读|未独立运行|1/3/专栏（对应机制）|已选读接口的其余实现未全审|
|`packages/subprocess/win32-process`<br>`@deepseek-ai/dsh-win32-process`|Shared low-level Win32 process, stdio, and Job Object primitives|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/telemetry/otel`<br>`@deepseek-ai/dsh-otel`|Cordis service for independent ordinary-event and byte-bounded Session-log OTLP channels|`src/index.ts`|关键实现深读（选段）|未独立运行|1（16项关注点补充）/专栏（对应机制）|选段核对；整包及真实模型／UI／完整部署未验证|
|`packages/terminal/terminal`<br>`@deepseek-ai/dsh-terminal`|Persistent PTY session seam for the DeepSeek Harness — owner-scoped ids, backend registry, interactive sends, reads, signals, and awaited cleanup|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/terminal/terminal-bash`<br>`@deepseek-ai/dsh-terminal-bash`|Persistent shell PTY backend over the DeepSeek Harness subprocess terminal primitive|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/terminal/tool-terminal`<br>`@deepseek-ai/dsh-tool-terminal`|Six model-facing persistent PTY tools with owner isolation and generic background-job integration|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/test-support/agent-loop-testkit`<br>`@deepseek-ai/dsh-agent-loop-testkit`|Prerequisite mounting, production AgentLoop drivers, and Inbox stubs for tests|`src/index.ts`|实现／接口选读|未独立运行|1/3|已选读接口的其余实现未全审|
|`packages/test-support/client-runtime`<br>`@deepseek-ai/dsh-client-test-runtime`|Browser test runtimes: a jsdom slot bench with test-owned Session and Workspace doubles, and a whole-client tier that boots the web roster through the production bootClient over an endpoint-named Remote mock|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/test-support/llm-mock-server`<br>`@deepseek-ai/dsh-llm-mock-server`|Scriptable Messages HTTP/SSE fault server for LLM recovery tests|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/test-support/llm-replay`<br>`@deepseek-ai/dsh-llm-replay`|Replay LLM plugin: short-circuits llm/stream with model chunks reconstructed from a recorded session JSONL (keyless snapshot tests)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/test-support/loader-smoke`<br>`@deepseek-ai/dsh-loader-smoke`|Shared subprocess and direct-agent harness for keyless real-Loader example smoke tests|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/test-support/remote-mock`<br>`@deepseek-ai/dsh-remote-mock`|Endpoint-named mock for Typert Remote traffic: unary answers and stream scripts per <namespace>/<method>, live stream control, a log, and the Connection carrier face whole-client specs install|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/test-support/session-snapshot`<br>`@deepseek-ai/dsh-session-snapshot`|Session-log snapshot core with an ACP protocol adapter, expected-output normalization, and fixture invariants|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/todo/tool-todo`<br>`@deepseek-ai/dsh-tool-todo`|Model-facing todo_write tool over the DeepSeek Harness event-sourced session log|`src/index.ts`<br>`tests/integration.spec.ts`|关键实现深读（选段）|V10：对应选定测试文件通过；非整包／完整应用验证|1（16项关注点补充）/2（运行关注点补充）/专栏（对应机制）|选段核对；未逐行审阅整包，真实模型／UI／完整部署未验证|
|`packages/typert/generator`<br>`@deepseek-ai/dsh-typert-generator`|TypeScript project analyzer and model-driven Typert artifact generator|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/typert/loader`<br>`@deepseek-ai/dsh-typert-loader`|Loader integration for generated Typert package contributions|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/typert/protocol`<br>`@deepseek-ai/dsh-typert-protocol`|Compiler-independent Remote metadata and Typert provider protocols|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/typert/registry`<br>`@deepseek-ai/dsh-typert-registry`|Runtime registry for generated package reflection and Zod schemas|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/atomic-write`<br>`@deepseek-ai/dsh-atomic-write`|Zero-dependency atomic file replacement: exclusive-create random-suffix temp + rename carrying the caller-stated permissions (writeFileAtomic)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/brand`<br>`@deepseek-ai/dsh-brand`|Stateless branded primitive types for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/chunked-list`<br>`@deepseek-ai/dsh-chunked-list`|Persistent append-only chunked lists with bounded copying and JSON checkpoint validation|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/code-language`<br>`@deepseek-ai/dsh-util-code-language`|Single file-extension to syntax-highlighting language table shared by Client code surfaces and the Host read card|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/crypto`<br>`@deepseek-ai/dsh-util-crypto`|Zero-dependency browser-safe UUID and byte-encoding helpers|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/deque`<br>`@deepseek-ai/dsh-deque`|Zero-dependency circular deque with amortized constant-time end operations and bounded vacant storage|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/home-paths`<br>`@deepseek-ai/dsh-home-paths`|Shared filesystem path helpers for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/http-proxy`<br>`@deepseek-ai/dsh-http-proxy`|Process-wide outbound HTTP proxy policy for DeepSeek Harness: resolve it from the launch environment and install it as undici's global dispatcher|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/launch-environment`<br>`@deepseek-ai/dsh-launch-environment`|Immutable DeepSeek Harness launch environment that records which layer supplied each value|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/lazy-require`<br>`@deepseek-ai/dsh-lazy-require`|Caller-relative, success-cached lazy loading for CommonJS-compatible Host dependencies|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/native-command`<br>`@deepseek-ai/dsh-native-command`|Host-native command and path-opening utilities with shell-free execution, cancellation, desktop detection, and WSL handoff|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/output-retention`<br>`@deepseek-ai/dsh-output-retention`|Zero-dependency bounded-retention primitive: ItemRetainer/TextRetainer + neutral notice helpers (what did we keep, what did we omit)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/package-manifest`<br>`@deepseek-ai/dsh-package-manifest`|Shared type declarations for package.json.dsh configuration fields|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/time`<br>`@deepseek-ai/dsh-util-time`|Zero-dependency time vocabulary shared by wire boundaries: canonicalClientTimeZone (IANA zone validation and canonicalization only, no formatting)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/timeout`<br>`@deepseek-ai/dsh-timeout`|Zero-dependency timeout/deadline primitive: clampTimeout, deadline, timeoutOf, TimeoutReason (timing + classification only, no termination)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/values`<br>`@deepseek-ai/dsh-util-values`|Duplicate-install-safe value primitives for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/util/workspace-path`<br>`@deepseek-ai/dsh-util-workspace-path`|Browser-safe Workspace path and display helpers|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/web/tool-web`<br>`@deepseek-ai/dsh-tool-web`|Model-facing web tools (web_search, web_fetch) over the DeepSeek Harness web capability seam (ctx.web)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/web/web`<br>`@deepseek-ai/dsh-web`|Abstract web access capability seam (ctx.web) for the DeepSeek Harness — search/fetch provider registry, registration-order-independent selection, request/result vocabulary, and the WebError taxonomy|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/web/web-fetch-http`<br>`@deepseek-ai/dsh-web-fetch-http`|Anonymous public HTTP(S) fetch provider for the DeepSeek Harness web capability seam (ctx.web)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/web/web-search-deepseek`<br>`@deepseek-ai/dsh-web-search-deepseek`|DeepSeek-backed search provider (native web_search via the Anthropic-compatible API) for the DeepSeek Harness web capability seam (ctx.web)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/web/web-search-exa`<br>`@deepseek-ai/dsh-web-search-exa`|Exa-backed search provider for the DeepSeek Harness web capability seam (ctx.web)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/web/web-search-perplexity`<br>`@deepseek-ai/dsh-web-search-perplexity`|Perplexity-backed search provider for the DeepSeek Harness web capability seam (ctx.web)|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/webhook/webhook`<br>`@deepseek-ai/dsh-webhook`|Fire-and-forget webhook rule runtime that creates Workspace-backed DeepSeek Harness Sessions|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/webhook/webhook-github`<br>`@deepseek-ai/dsh-webhook-github`|Signed GitHub HTTP webhook adapter for the DeepSeek Harness webhook runtime|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/workflow/tool-ralph`<br>`@deepseek-ai/dsh-tool-ralph`|Model-facing fresh-agent Ralph loop over the workflow and subagent seams|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/workflow/tool-workflow`<br>`@deepseek-ai/dsh-tool-workflow`|Model-facing workflow tool: run a JavaScript orchestration script over ctx.workflowEngine|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/workflow/workflow`<br>`@deepseek-ai/dsh-workflow`|Workflow capability seam: ctx.workflowEngine service, run vocabulary, and workflow/* events|`src/index.ts`|实现／接口选读|未独立运行|1/3|已选读接口的其余实现未全审|
|`packages/workflow/workflow-ptc`<br>`@deepseek-ai/dsh-workflow-ptc`|Workflow orchestration in the shared sandboxed Node PTC runtime|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`packages/workspace/workspace`<br>`@deepseek-ai/dsh-workspace`|Workspace entity registry (ctx.workspaceRegistry): durable workspace records with validated session attachment over the domain data form for the DeepSeek Harness|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`python/sdk-runtime`<br>`dsh-python-runtime-closure`|Dependency-only deploy root defining the dsh executable shipped by the Python runtime wheel.|`README.md`|配置／说明概览|未独立运行|1（盘点）|实现与运行行为未深核|
|`vendor/cordis`<br>`@deepseek-ai/cordis`|Meta-Framework for Modern JavaScript Applications|`src/context.ts；src/fiber.ts；src/events.ts；src/reflect.ts`|关键实现深读（选段）|V01/V05消费者验证|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`vendor/cosmokit`<br>`@deepseek-ai/cosmokit`|A collection of common utilities|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`vendor/group`<br>`@deepseek-ai/cordis-plugin-group`|Nested plugin group for cordis|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`vendor/hmr`<br>`@deepseek-ai/cordis-plugin-hmr`|Hot Module Replacement Plugin for Cordis|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`vendor/include`<br>`@deepseek-ai/cordis-plugin-include`|Include files in cordis configurations|`src/index.ts`|关键实现深读（选段）|未独立运行|1/2/3|目标部署／真实provider与完整suite未验证|
|`vendor/loader`<br>`@deepseek-ai/cordis-plugin-loader`|Plugin loader for cordis|`src/index.ts`|关键实现深读（选段）|未独立运行|1/2/3/专栏（对应机制）|目标部署／真实provider与完整suite未验证|
|`vendor/logger-console`<br>`@deepseek-ai/cordis-plugin-logger-console`|Console logger exporter for cordis|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`vendor/schemastery`<br>`@deepseek-ai/schemastery`|Type driven schema validator|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`vendor/timer`<br>`@deepseek-ai/cordis-plugin-timer`|Timer service for cordis|`src/index.ts`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|
|`website`<br>`@deepseek-ai/website`||`package.json`|仅清单盘点|未独立运行|1（盘点）|实现与运行行为未深核|

## 生成、资源、夹具与读取限制

- 生成catalog、Remote类型和golden文件：在关键兼容／迁移契约处按需追踪；不手改生成输出。
- vendor：不是排除项，Cordis/Loader/Include已追踪；其它第三方只按依赖需要查看。
- snapshot、测试fixture：用于已有测试解释；未把fixture输出当真实生产数据。
- node_modules、lib、native binaries与构建缓存：不在git tracked基线清单，构建用于验证，不当手写源码盘点。
- 图片、字体、翻译资源、网站静态内容：完整路径盘点；不逐个视觉检查，原因是本任务聚焦运行与扩展契约。
- Python、Windows/Linux、experimental Team/Worker、实际UI：列入研究边界并说明接口／来源，但不是本机运行通过。

初次研究的读取日志包含 71 个不同路径的 range 请求；本轮补充选段另见 E78—E119。这些初次请求；仅作可复核线索，不给出“读了百分之几源码”的误导数字。完整路径见[tracked-files](tracked-files.txt)，机器清单见[workspace-inventory](workspace-inventory.json)，每包深度JSON见[coverage.json](coverage.json)。

## 架构补充阅读范围（同 SHA）

本轮新增 E78—E119 共 42 条固定源码／文档锚点，按目标、模型适配、MCP、作业、遥测、测试、交付和格式兼容追踪局部机制。逐包表同步记录选读路径；阅读范围仍是选段，不能当作整文件或全仓逐行覆盖。非工作区包的官方材料包括 `docs/testing.md`、`docs/subsystems/session-telemetry.md`、`docs/user/guide/mcp-memory.md`、`docs/session-format-status.md` 与 benchmark README。V08 只验证 7 个明确列出的测试文件，不外推到其他包、完整 profile、线上服务或其他平台。
