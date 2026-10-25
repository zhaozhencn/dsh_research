# DSH 插件扩展开发：2026-10-25 更新版

本轮以 AI 架构设计与开发教学为主线，更新插件扩展相关研究。当前源码 **`0.2.1-rc.3` / `22ddee3792402c3e70ec5f86a63c3e3e895a2f60`**，来自当日在线发现的官方 `master`；旧版 `5badb15009ae1756c3afe0ae0cef1faafc290ccc` 的报告、示例与图片保留在上级目录。

## 阅读入口

|目标|文档|
|---|---|
|决定业务能力、Host/Agent/UI/权限放在哪层|[第一篇：架构与职责](01-architecture.md)|
|追踪创建、准入、模型选择、工具执行和退出|[第二篇：源码运行链](02-runtime-source.md)|
|开发、复现和交付两个插件|[第三篇：扩展开发实践](03-extension-practices.md)|
|从旧文档迁移|[版本差异与旧文阅读指引](appendices/delta.md)|
|查接口、挂载和退出责任|[当前扩展契约矩阵](appendices/extension-contract-matrix.md)|
|复现实验|[示例与环境准备](examples/README.md) · [验证记录](appendices/validation.md)|
|审查结论|[源码基线](appendices/baseline.md) · [证据索引](appendices/evidence-index.md) · [覆盖](appendices/coverage.md) · [待验证项](appendices/open-questions.md)|

## 直接影响插件的变化

1. 在准备 Step 前用 `agent.model.select()` 选择模型；旧 `agent/request` 路由改写会被拒绝。
2. Native/PTC 由独立 executor 插件提供；自定义 runtime 需要显式挂载。
3. 条件工具通过 `register(..., { when })` 统一准入；已撤销定义不能被旧 Step 复活。
4. 投影注册改为 await 后持有 handle；Remote 已有 Peer principal 和逐资源访问决策。
5. 兼容声明优先 `engines.dsh`；Client 的模块依赖与 Cordis 服务激活分别设计。

上述变化的源码与测试定位位于三篇正文和差异附录。本轮盘点 **386 包 / 19,188 tracked 文件**；不把未读实现计入深读。新版两个插件严格类型和编译通过，**8 项真实 Loop 集成测试通过**；选定 **13 个上游测试文件、284 项通过**，与历史用例及重跑不累加。

本轮完成范围是插件扩展开发相关同步，交付保证级别为 **limited**：未做整仓构建、全部机制审计、真实模型/企业后端、浏览器 E2E、tarball 安装和跨平台验证。不能把上级目录 alpha.1 的运行结果或企业示例直接视为 rc.3 已通过。上级 29 篇专栏保留为历史研究，逐篇迁移位置见 delta。
