# 覆盖范围

全量盘点不等于逐行审计。386 个 workspace manifest 与 19,188 个 tracked 路径来自目标提交；包职责取 manifest description，不能作为实现深读证据。深读仅限插件开发的装配、准入、模型选择、执行器、取消、投影、Remote 和产物消费等路径。

|包/区域|本批实现阅读|验证层|
|---|---|---|
|`packages/api/gateway`|1 个文件的指定片段|源码/官方说明|
|`packages/api/remote-access`|1 个文件的指定片段|选定测试|
|`packages/boot/app-boot`|1 个文件的指定片段|选定测试|
|`packages/boot/config-editor`|1 个文件的指定片段|源码/官方说明|
|`packages/boot/plugin-manager`|1 个文件的指定片段|选定测试|
|`packages/client/modules`|1 个文件的指定片段|源码/官方说明|
|`packages/core/agent`|2 个文件的指定片段|选定测试|
|`packages/core/agent-loop`|3 个文件的指定片段|选定测试|
|`packages/core/session`|1 个文件的指定片段|源码/官方说明|
|`packages/core/tool-executor-native`|1 个文件的指定片段|源码/官方说明|
|`packages/core/tools`|4 个文件的指定片段|选定测试|
|`packages/session/session-persistence`|1 个文件的指定片段|源码/官方说明|
|`packages/session/session-projection`|2 个文件的指定片段|选定测试|

未列出的包为 manifest-only；完整逐包标记、路径、片段及 reviewed_at_sha 见 [coverage.json](coverage.json)。各章节引用的范围都有 read-ranges，不将工具截断输出计为全文件已读。

|非 workspace 区域|处理方式|
|---|---|
|`docs/`|重点读当前架构、工具/包 cookbook、相关 upgrade guides、Remote 规则；其他文档仅索引|
|`vendor/`|读 manifest、注册纪律并编译 Cordis/Schemastery 声明；没有重新逐行审计 vendor|
|`scripts/`、根配置|读测试/装配与构建命令；未审计所有 gates 实现|
|`.agents/`|架构 notes 仅定位线索；未作为产品运行结果|
|`native/`|运行目标 host addon 构建；未审计全部原生实现|
|`python/`、`snapshots/`、`website/`|tracked 盘点；未宣称 Python SDK、录制快照或网站构建验证|
|`patches/`、assets、生成文件|依赖与产物盘点；不计源码深读|
