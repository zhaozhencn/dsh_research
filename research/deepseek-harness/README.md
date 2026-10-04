# DeepSeek Harness 固定版本源码研究

已按任务书完成三篇中文研究、完整工作区盘点、源码证据与提交追踪，以及两个经过类型检查、编译和真实Agent Loop离线验证的扩展。研究由单一执行者完成，没有委派研究子代理或人工确认节点。

基线：**2026-10-04／0.2.1-alpha.1／`5badb15009ae1756c3afe0ae0cef1faafc290ccc`**。341 workspace成员，14,208 tracked文件；完整盘点不意味着逐行阅读全部文件。核心深读与外围manifest盘点分别记录。

|成果|阅读用途|
|---|---|
|[第一篇：宏观架构](01-architecture.md)|架构总览及 16 项关注点：任务、模型、状态、治理、评测与交付|
|[第二篇：源码运行](02-runtime-source.md)|沿 16 项关注点追踪调用、状态提交、失败恢复及具体场景|
|[第三篇：二次开发](03-extension-practices.md)|扩展契约、替换矩阵、私有工作台方案、示例及落地验收|
|[16 篇技术专栏](articles/README.md)|每项关注点独立展开：架构、源码、异常过程、取舍与技术心得|
|[研究基线](appendices/baseline.md)、[覆盖清单](appendices/coverage.md)|环境、版本与逐包阅读／验证范围|
|[证据索引](appendices/evidence-index.md)|149 条固定 SHA 源码／文档锚点、4项实际提交diff、运行证据|
|[验证记录](appendices/validation.md)、[遗留问题](appendices/open-questions.md)|复现命令、失败修复、完成边界与上线前最小动作|
|[两个扩展示例](examples/README.md)|工具、request route policy；源码、独立包、JS、patch及测试|

本次按 16 项公共关注点完善第一篇，新增 42 条证据锚点，并明确目标完成与独立验收、回合额度与累计成本、反馈授权遥测与实时追踪、临时变更视图与持久产物的区别。上游 SHA 保持不变，属于同版本研究补充。

第二篇随后按同样的 16 项补充运行链路，新增 29 条源码锚点，重点解释目标准入、模式提交、压缩重试、作业清理、遥测交接与产物恢复，并保留原有 Loop 和持久化分析。

本轮新增 16 篇独立技术文章、16 张 PNG 机制图及对应可编辑 SVG。关键代码取自固定提交，专栏沿用既有运行证据，不增加测试计数；反馈授权证据 E147 的源码位置已校正，另补 E149 的交接游标依据。

主要发现：

1. 产品能力通过Cordis组合，具体Loop本身也是插件；Context仍有框架基础，Scope／realm不是租户安全隔离。
2. Session事实日志、模型surface、projection与live assistant stream分工明确；内存append和whenIdle不等于磁盘flush。
3. 工具prepare有序、body有限并发、结果按模型序提交；超时等到底层quiescence，依赖工具响应取消。
4. resume／fork重建和修补事件边界，工具未知结果不会自动盲重跑；外部副作用没有统一回滚保证。
5. 配置刷新与模块HMR是不同能力，默认因profile而异；局部激活失败不能泛称全局事务rollback。
6. route插件卸载只撤销listener，已有Session的logged route仍可保持；新Agent与已有会话必须分别验证。

累计去重验证：**36 个测试文件，1,504 passed、1 conditional skipped**，包含 35 个仓库文件和 1 个自定义测试文件。初次缺native flock导致154失败，按仓库流程构建后受影响suite全部通过，原始失败日志保留。两个插件的编译JS实际执行了5个正常／参数错误／路由／作用域／取消场景。本次架构补充另运行 7 个不重复的仓库测试文件，201 passed、0 failed/skipped；本次运行补充又执行 6 个不重复仓库文件，302 passed、0 failed/skipped。原有失败与修复记录保留。详细计数见 validation，未运行全仓测试或宣称覆盖率。

限制：真实模型服务、完整profile／发布包安装、Web与Electron E2E、Linux/Windows执行沙箱、Pythonwheel、性能与企业多租户授权均未实测。报告明确分开源码事实、官方说明、运行验证、分析推断和改造建议，关键结论可沿固定SHA链接复核。

源码checkout位于工作区`.sources/deepseek-harness`，报告不复制整仓。源码tracked状态保持干净；构建输出、依赖安装与研究材料各自保留。全部交付文件与Mermaid语法检查结果见[artifact-check.json](validation/artifact-check.json)。
