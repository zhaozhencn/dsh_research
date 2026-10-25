# 条件求和工具

适用固定 SHA `22ddee3792402c3e70ec5f86a63c3e3e895a2f60`，DSH 0.2.1-rc.3、Cordis 4.0.5、Schemastery 3.18.5。独立 ESM 插件，入口 `lib/index.js`，源码 `index.ts`。

插件以 `{when}` 按 Step 决定可调用性，Config.enabled 默认 true；输入 a/b 校验后返回 canonical number，render 为模型文本。无共享副作用，允许并发。调用前响应取消，卸载撤销定义。

从研究仓库根目录按[环境准备](../README.md)执行 typecheck、build、test。预期 2+3 的 5 进入下一模型 Step；非法输入 INVALID_ARGS；禁用与准入后卸载返回 UNKNOWN_TOOL。其余 8 项用例覆盖策略与取消，不另重复计数。

目标 profile 应已有 tools 和 Native/PTC executor；这个工具包不再额外挂 executor。安装/激活步骤见上级说明。本批测试编译产物配源码 aliases，未验证 tarball/install consumer；未验证真实模型或 UI。结束进程后移除自己创建的临时 home 即可，不删除正式配置。
