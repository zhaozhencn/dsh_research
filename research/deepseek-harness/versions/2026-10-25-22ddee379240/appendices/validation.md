# 本轮验证与可复现性

源码统一为 `22ddee3792402c3e70ec5f86a63c3e3e895a2f60`，独立 worktree；实际 Node 24.19.0，pnpm 11.28.5。执行前 HEAD 与 tracked 源码一致，未修改受测上游源码。参考插件编译 ESM，运行由 fixed-SHA 源码 alias 提供真实 Cordis/Session/LLM/Loop/Native executor；只有模型流使用可控 fixture。

## 结果与层级

|执行|结果|能支持的结论|
|---|---|---|
|frozen-lockfile install / host native / vendor declarations|各退出 0|本机选定测试环境可准备；不是全仓 build|
|参考扩展严格类型|退出 0|两个插件与 fixture 的当前导入/签名可检查|
|参考插件 ESM 编译|退出 0|两包 lib/index.js 生成，bare imports 保留|
|真实 Loop 集成|8 passed，0 failed，0 skipped|工具结果续接、invalid args、条件禁用、旧集撤销、选模时点、scope、卸载、流取消|
|选定上游回归|13 文件 / 284 passed，0 failed，0 skipped|所选模型/工具/取消/投影/兼容/patch/访问 policy 行为|
|研究结构与源码锚点|通过：40 条证据、386 包、165 个当前源码链接；见 logs/artifact-check.log|文件/范围/hash/版本与链接一致性|
|Mermaid 语法|2 张通过；parser 11.17.2；见 logs/diagrams.log|图的语法解析；不等于 UI 截图|

完整命令、cwd、退出码、输入、预期、实际和限制见 [runs.json](../validation/runs.json)；默认/JSON reporter 记录分别为 [上游日志](../validation/logs/upstream.log)、[上游逐项结果](../validation/upstream-results.json)、[扩展逐项结果](../validation/extensions-results.json)。参考扩展复现入口为 [check.mjs](../validation/check.mjs)。vendor-types 初次输出为空，但执行工具明确返回 0；不能以“日志为空”独立证明成功。

## 失败、修正与计数

初次安装命令的日志父目录不存在，shell 在重定向阶段返回 1，pnpm 尚未执行；随后创建 validation/logs 再安装成功。失败原文另存 [setup failure](../validation/logs/install-setup-failed.log)。未把这一失败称为产品缺陷。

参考策略最初额外安装了 model-switch 提示 listener；审查后移除，由宿主或 setup 按需装一次，避免重复。源码变更后重跑对应类型、build、8 项测试，均通过。每次日志分开保存；集成只计最终 8 个 unique 用例，上游独立计 284 个参数实例（280 个不同文件/标题，四组 null/undefined 参数显示同标题，逐项索引见 validation/test-case-index.json），不累加重跑，不叠加旧 alpha.1 的 1,520 或补充批次 848。

## 验证边界

本批没有整仓 build:artifacts/build:check、真实模型/企业后端、网络 Gateway E2E、浏览器 UI、tarball 发布安装、Python SDK、业务存储迁移或跨平台 sandbox 测试。上游 AGENTS 对代码开发的完整 build 要求没有被本研究宣称满足；本轮改的是本仓研究与参考插件，仅对本轮可复现例子作类型/编译/运行保证。

RemoteAccess host 单测证明 policy 实现的选定行为；不能证明连接握手、所有 Remote 方法资源标注都完整。Native 测试也不能证明 PTC runtime、SSH 或系统隔离。因此 state.assurance 为 limited，范围见[待验证项](open-questions.md)。

总校验脚本已支持版本目录：历史区域保持原 SHA，versions 下逐版调用各自固定基线检查和 Mermaid parser；本次完整入口退出 0。结果见 [root-artifact-check.json](../validation/root-artifact-check.json)。可选第二位置参数用于写本次结果，避免覆盖历史 canonical JSON。
