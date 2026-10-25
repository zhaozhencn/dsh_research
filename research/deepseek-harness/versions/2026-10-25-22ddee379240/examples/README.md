# 新版插件复现与接入

固定源码 `22ddee3792402c3e70ec5f86a63c3e3e895a2f60` / DSH 0.2.1-rc.3；Node 24.19.0、pnpm 11.28.5、Cordis 4.0.5、Schemastery 3.18.5。两个包分别为[条件工具](sum-tool/README.md)与[模型策略](route-policy/README.md)。

## 环境准备

下面从本研究仓库根目录运行，在 `.sources/` 使用独立源码。若目标目录已经存在并正确固定 SHA，跳过 clone/checkout；不要覆盖正在开发的 checkout。

```sh
git clone https://github.com/deepseek-ai/deepseek-harness .sources/deepseek-harness-2026-10-25
git -C .sources/deepseek-harness-2026-10-25 checkout --detach 22ddee3792402c3e70ec5f86a63c3e3e895a2f60
cd .sources/deepseek-harness-2026-10-25
corepack pnpm install --frozen-lockfile --ignore-scripts
corepack pnpm run build:native-system
corepack pnpm exec tsc -b vendor/cordis vendor/schemastery
cd ../..
node research/deepseek-harness/versions/2026-10-25-22ddee379240/validation/check.mjs typecheck
node research/deepseek-harness/versions/2026-10-25-22ddee379240/validation/check.mjs build
node research/deepseek-harness/versions/2026-10-25-22ddee379240/validation/check.mjs test
```

本轮为固定依赖的源码测试选择 ignore-scripts，并显式准备 host addon 与 vendor 声明；这不是一般发行安装的默认建议。上游 build:native-system 不等于全仓构建。

`check.mjs` 可通过第三参数指定源码绝对目录，并拒绝不匹配的 HEAD。它不切换任何源码；typecheck 检查两插件及 fixture；build 用 TypeScript 单文件转译保留 bare imports；test 使用编译 JS 与同提交源码 aliases，避免嵌入第二份 runtime。预期 8 passed，测试和失败/重跑日志均在 validation。运行时全部 handle/Fiber 在 finally 内释放，临时配置由脚本删除。

## 真实 profile 接入（操作说明，本批未执行）

准备与源码同版的完整已构建 `dsh`；对生产 provider/model 作实际校验。先在终端设置报告绝对路径和临时 home：

```sh
export DSH_RESEARCH_EXAMPLES="$PWD/research/deepseek-harness/versions/2026-10-25-22ddee379240/examples"
export DSH_HOME="$(mktemp -d -t dsh-plugin-research)"
dsh plugin --profile sdk add "$DSH_RESEARCH_EXAMPLES/sum-tool" "$DSH_RESEARCH_EXAMPLES/route-policy"
dsh --profile sdk --patch "$DSH_RESEARCH_EXAMPLES/profile.patch.yml" --dump-config
```

patch 中 provider=mock/model=policy **仅用于本报告 fixture**。真正启动 SDK 前将它改为目标 profile 已注册且授权的路线，或只启用求和插件。SDK 需要 client 发送协议请求；这些准备命令不证明模型调用与包激活已通过。

`package.json` 定义 exact engines.dsh 与 peers；安装是包可解析，patch 是插件激活，两步分别确认。profile 若使用 preset，应按目标 preset 的覆盖规则限定能力，不把部署级插件误作会话隔离。

清理时先停止自己启动的 SDK 进程，确认临时 home 路径后仅删除那个目录，unset DSH_HOME；不要清理正式 home。编译输出只在两个示例的 lib，可通过 build 覆盖。参考扩展没有数据库或远程业务副作用。
