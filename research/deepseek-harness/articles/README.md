# 从源码理解 Agent Harness：架构、实现与工程取舍

这套专栏以 DeepSeek Harness 为研究对象，围绕 16 项公共关注点解释技术架构、关键实现、正常与异常执行、优势和不足，并提炼适用于 Agent 系统设计的工程认识。文章面向有开发经验、希望理解或建设 Agent 系统的工程师与架构师，每篇可以独立阅读。

研究基线为 **`0.2.1-alpha.1`／`5badb15009ae1756c3afe0ae0cef1faafc290ccc`**。文章在[源码运行报告](../02-runtime-source.md)基础上重新组织论证并复核关键实现，没有切换上游版本，也没有将项目尚未提供的能力写成现状。教学场景、源码事实、既有运行结果和应用改造建议分别表述。

## 16 篇文章

|篇次|文章|阅读重点|
|---|---|---|
|01|[任务何时才算完成：目标、Turn 与业务验收](01-task-completion.md)|27 段源码逐段解读，追踪创建、调度、接纳、取消与业务验收|
|02|[一次输入如何推进为多步执行：拆解 Agent Loop](02-agent-loop.md)|14 个连续步骤、38 段源码；核心数据、调用衔接与实现心得|
|03|[接入不同模型：路由绑定、能力解析与消息适配](03-model-adaptation.md)|PreparedLlmCall、精确能力、历史适配与异常归属|
|04|[模型每次究竟看到什么：上下文组装与压缩](04-context-engineering.md)|日志与 surface、上下文时机、选区配对与恢复进展|
|05|[进程重启之后：Agent 的状态、记忆与持久化](05-state-persistence.md)|JSONL、写所有权、checkpoint、恢复与缓存边界|
|06|[一次工具调用的完整生命周期：从参数到结果](06-tool-runtime.md)|输出契约、prepare／dispatch／finalize、观察与 provider|
|07|[失败之后如何继续：重试、取消与副作用一致性](07-reliability.md)|normal／always、协作取消、unknown 与幂等责任|
|08|[哪些工作可以同时执行：工具、作业与子 Agent 调度](08-concurrency.md)|并行 body、有序提交、stopping 配额与父子生命周期|
|09|[模型的行动权限从哪里来：审批、作用域与沙箱](09-security.md)|ask fail-closed、资源检查、来源权限与控制面|
|10|[如何控制自动推进：规划模式、目标续跑与人工接管](10-autonomy.md)|计划批准、pending intent、模式提交与撤销执行权|
|11|[限制 Turn 数为什么仍可能失控：成本、延迟与预算](11-budgets.md)|额度作用域、用量口径、输出预留与任务级预算|
|12|[如何还原 Agent 的行动：事实日志与反馈授权遥测](12-observability.md)|反馈授权、前缀捕获、脱敏、游标与远端确认|
|13|[如何证明 Agent 运行正确：契约测试与业务验收](13-evaluation.md)|真实 runtime、工具回流、取消断言与外部结果|
|14|[插件如何安全参与运行：依赖、事件与生命周期](14-plugin-lifecycle.md)|服务角色、waterfall、Fiber、卸载与存量状态|
|15|[如何把执行结果交给用户：协议、重连与交付物](15-interaction-deliverables.md)|接纳身份、baseline、live stream、文件与临时 diff|
|16|[Agent 系统如何持续演进：部署、兼容与状态迁移](16-deployment-evolution.md)|profile、激活审计、HMR、格式迁移与有序退出|

## 怎样阅读

顺序阅读可以从任务语义走到运行、治理和版本演进。若关注核心执行，可先读 02、03、04、06、07；若关注生产化，可先读 05、08、09、11、12、16；若负责产品集成，可先读 01、10、13、15，再回看相应实现。

各篇先说明整体机制，再以 caller、交接数据与返回结果连接关键步骤。核心结构提供固定SHA的原文选段、字段表与消费位置；正常路径、异常支线和装配生命周期明确区分。代码仅统一缩进，是原实现的局部选段；第13篇另引用既有研究验证代码。15篇沿第02篇标准修订后，主体关注领域和全部既有摘录保留，结尾分别提炼与正文对应的实践收获。第一篇现有27段，第02篇38段，其余各篇19—25段。完整实现可沿源码链接和[证据索引](../appendices/evidence-index.md)继续阅读。

技术心得来自代码选择与限制，例如：预算应覆盖真正耗资源的执行层级；取消请求与清理完成分别计量；事实记录与请求优化使用不同表示；扩展卸载分别处理贡献、状态和在途工作。它们是有前提的工程判断，不作为项目保证或无条件最佳实践。

## 图片与发布使用

16篇正文各嵌入4张PNG，共64张，并提供同名SVG。其余15篇的60张图已按最新阅读逻辑重绘与重新分布，第02篇保持原样。图示分别服务整体地图、关键交接、核心数据或寿命、条件分支，插在对应步骤附近；Agent、Turn、Step、attempt、Inbox、surface、Fiber 与源码类型标识保留英文。并列资源与成本关联不画成固定顺序调用，企业扩展明确标为建议。每张宽1200像素。图注与相邻源码共同说明范围，不能当作全量调用图；完整清单见[图示清单](assets/diagrams.json)，补充图的节点、步骤位置与摘录引用见[显式图定义](assets/diagram-supplements.json)。

文章正文采用短段落、小标题、局部代码和固定提交源码链接，适合转入图文编辑器。发布时使用对应 PNG，保留源码出处和基线；本地“上一篇／下一篇／附录”链接可按实际专栏地址替换。Markdown 文件是内容交付，不代表已经写入或发布到公众号。

若继续修改图示，先修改对应定义，再运行[完整绘图入口](../validation/build-column-assets.py)，该入口会调用[补充绘图脚本](../validation/build-column-supplements.py)。本机使用Pillow和系统中文字体；其他平台通过DSH_COLUMN_FONT指定中文字体。PNG与SVG共用几何定义，渲染器检查文字宽度与纵向边界。图片已检查解码、尺寸及SVG结构，另查看三组总览与代表性单图；未在公众号编辑器中预览或发布。

```sh
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/build-column-assets.py
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-column.py
node research/deepseek-harness/validation/check-artifacts.mjs
```

上述虚拟环境是本机复现路径，其他环境需先安装Pillow。

## 证据与验证范围

初次专栏写作沿用原研究同一SHA的测试证据，当时累计36个文件、1,504 passed、1条条件skip；企业示例后累计为**37个文件、1,520 passed、1条条件skip**。第一篇深化、全系列扩写、第02篇修订和本次15篇同步完善均未新增或重跑行为测试。各历史批次与限制保存在验证附录中。已有完整正常／异常链、扩展编译、类型和选定子系统结果见[验证附录](../appendices/validation.md)。真实模型、完整发布安装、浏览器、跨平台沙箱和企业授权未由离线结果证明。

首次写作有33段代码，第一篇深化后为54段，全系列深化时为298段；第02篇叙事及结构补充后为316段。本次为其余15篇增加48段核心数据与状态原文，当前共**364段**。机器检查核对16项映射、显式标题约定、主体章节数量、逐段原文及hash、固定SHA与行号、每篇4图的顺序和位置、英文术语、链接、PNG/SVG及既有Mermaid。结果见[专栏检查](../validation/column-check.json)，摘录与篇章关系见[专栏清单](../validation/column-manifest.json)。这些检查验证可定位性与一致性，源码解释和图示关系由单一执行者另行复核。

历史记录保留：[全系列深化](../validation/series-deepening-review.json)、[第02篇叙事修订](../validation/agent-loop-review.json)、[第02篇结构与行文优化](../validation/agent-loop-refinement-review.json)。本次范围、逐篇新增结构、保留情况和验证命令见[15篇同步完善记录](../validation/series-refinement-review.json)；当前标题及图序见[编辑修订约定](../validation/column-editorial-revisions.json)。

研究重查修正 E147 的反馈授权实现位置，并补充 E149 的进程内交接游标证据；这属于原基线证据完善，不是上游功能新增。
