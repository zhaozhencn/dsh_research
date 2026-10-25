# 源码基线与环境

- 官方仓库：[deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)。
- 查询时点：2026-10-25T11:18:23.996178+00:00（北京时间 19:18:23）；方式 `git ls-remote --symref`。
- 官方默认 ref：`refs/heads/master`；固定 SHA：`22ddee3792402c3e70ec5f86a63c3e3e895a2f60`；提交时间 2026-10-23T19:48:59+08:00。
- 当前提交 package.json 声明 `0.2.1-rc.3`，不是“最新稳定发行”的判定。
- 旧 SHA：`5badb15009ae1756c3afe0ae0cef1faafc290ccc`，声明 `0.2.1-alpha.1`；旧研究无 research-state，按 `legacy-ungraded` 导入。
- 祖先关系已确认：旧提交是新提交祖先，中间 3,198 个提交。`git diff --shortstat` 为 9,840 文件变化；rename 识别口径不同不直接等于 changes.json 记录数。
- tracked 文件 19,188；workspace 包 386（旧 341），按包名比对新增 46、删除 1；全量清单来自提交对象。

实际 Node `v24.19.0`，声明 Node `>=24.9.0`；checkout 内 corepack 使用声明的 `pnpm@11.28.5`。研究仓库外层的 pnpm 版本不作为目标安装版本。TypeScript 6.0.3、Vitest 4.1.11、Mermaid 11.17.2；Cordis 4.0.5、Schemastery 3.18.5。锁文件随源码固定，依赖安装使用 frozen lockfile。

独立 worktree 为 `.sources/deepseek-harness-2026-10-25`；旧 `.sources/deepseek-harness` 不切换。`--ignore-scripts` 安装后，按目标代码规则构建 host native addon 与 vendor declarations。没有运行整仓 build，不把局部构建写成产品构建完成。正式运行前仍需正常构建/安装产物。

快照数据、resolution、tracked 列表、动态 workspace 与 manifest 依赖图均保留在本目录；源码深读范围另见 [coverage](coverage.md)。
