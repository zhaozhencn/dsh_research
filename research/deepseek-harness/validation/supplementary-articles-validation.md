# 补充专栏17—28：来源、编辑与运行验证

本批按[文档列表与大纲](../appendices/supplementary-article-outlines.md)完成12篇补充文章，每篇保留八个主体章节，沿真实交接对象解释源码、失败与退出路径，并加入工程心得和四张分散配图。文章入口见[专栏目录](../articles/README.md#补充专栏17—28)。

## 来源与完成范围

源码固定于 DSH `0.2.1-alpha.1`，提交 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。摘录直接读取本地 Git 对象；原文仅移除公共缩进，不把教学示例当成上游实现。26、27篇引用的企业扩展属于本仓库示例，在来源清单中单独标注 `repository-enterprise-example`。

初次交付包括12篇正文、148段附行号源码、48组1200×1400 PNG/SVG图、12份逐篇梳理，以及扩展契约、端到端参考示例和变更回归三份配套文档。逐篇梳理先于正文写入，最终复核状态记录在 [supplementary-article-plans](supplementary-article-plans)。

以下文件提供当前版本的可追溯入口：

- [来源与资产清单](supplementary-articles-manifest.json)：摘录、行范围、分类、原文hash和图文对应。
- [源码与结构检查结果](supplementary-articles-check.json)：固定提交、引用原文、八章节、图序、链接、PNG解码、SVG尺寸及原文件保护。
- [保护基线](supplementary-protected-baseline.json)：生成前原00—16篇及相关资产的156项hash；目录README不在保护范围。
- [运行记录](supplementary-runtime-runs.json)：测试选择、版本、退出码与日志。

文章另行逐篇阅读，补充关键对象对照和具体竞态示例，MCP调用解读回到工具执行章节，resources与instructions随后独立展开。全部48张配图通过四图联系表检查；对MCP、企业接入和构建图补看原尺寸。自动检查验证来源和结构，不能替代调用关系、解释准确性及阅读体验的人工式复核。

本轮逐篇复核补充3段固定提交原文，当前共151段，原148段全部保留；修正内容和本轮文稿检查见[逐篇复核](supplementary-articles-review.md)。下方848项测试属于生成批次，本轮没有重跑。

## 本批实际运行

环境为 Darwin、Node `24.19.0`、pnpm `11.7.0`、Vitest `4.1.8`。上游测试使用固定 checkout 的已安装 Vitest；运行PATH中的本地wrapper将测试内部的pnpm调用固定到`11.7.0`。下表按独立运行计数，与历史1,520项存在重叠，不累加。

|范围|测试文件|通过|跳过|退出码|日志|
|---|---:|---:|---:|---:|---|
|17—20：创建、Skill、设置、包管理|11|372|0|0|[上游测试](supplementary-article-runs/test-17-20-pinned.log)|
|21—24：Client、Gateway、SDK、ACP、MCP、PTC|16|274|1|0|[上游测试](supplementary-article-runs/test-21-24.log)|
|25、27：Workflow、Schedule、Hooks、请求信任、凭据|8|131|0|0|[上游测试](supplementary-article-runs/test-25-27.log)|
|26、28：SSH providers、退出协议、构建脚本契约|6|55|0|0|[上游测试](supplementary-article-runs/test-26-28.log)|
|本仓库enterprise compiled integration|1|16|0|0|[扩展测试](supplementary-article-runs/enterprise-test.log)|

共848项通过、1项跳过。跳过的是PTC runtime的Windows grant-lock/private-native-temp用例；本机为Darwin，满足其`process.platform !== 'win32'`跳过条件。其余沙箱用例没有因此一并被算作验证完成或忽略。

参考扩展另行完成strict typecheck、ESM build和本地pack消费，均退出0：

```sh
# 本研究仓库根目录
node research/deepseek-harness/validation/enterprise-example.mjs typecheck
node research/deepseek-harness/validation/enterprise-example.mjs build
node research/deepseek-harness/validation/enterprise-example.mjs test
node research/deepseek-harness/validation/supplementary-pack-smoke.mjs
```

日志：[typecheck](supplementary-article-runs/enterprise-typecheck.log)、[build](supplementary-article-runs/enterprise-build.log)、[pack consumer](supplementary-article-runs/packed-smoke.log)。[pack检查结果](supplementary-pack-check.json)记录tarball清单、hash与exports路径存在性。独立解包目录实际导入的是`./ledger`：检查receipt重试一致、重开SQLite后保留、业务audit仅提交一次。其他plugin exports仍需要其声明的精确peer dependencies；exports文件存在不等于全部exports均已导入成功。

## 保留的失败与修正

第一次上游启动因没有可用的直接pnpm命令失败，退出127，见[初次日志](supplementary-article-runs/test-17-20.log)。随后改用checkout的Vitest，包管理测试中的真实pnpm构建审批fixture仍失败，371项通过、1项失败，退出1，见[直接启动日志](supplementary-article-runs/test-17-20-direct.log)。

临时Corepack shim在fixture目录使用了与checkout不一致的pnpm默认版本，构建审批fixture仍失败，见[准备环境后的失败日志](supplementary-article-runs/test-17-20-ready.log)。将子命令wrapper固定为上游声明的`pnpm@11.7.0`后，该组372项全部通过。以上运行保留原样；最终通过不会覆盖早期失败，也不会被解释为修复了上游业务源码。

首次结构检查将正文中的索引函数调用表达式误识别成Markdown链接，并将“反向代理”命中Agent术语关键词。已把前者改写为明确的函数与参数说明，后者保留英文`Reverse Proxy`；原源码摘录未改动。保留[补充检查首轮日志](supplementary-article-runs/supplementary-check-first.log)、[链接检查首轮日志](supplementary-article-runs/artifact-check-first.log)和[原专栏检查首轮日志](supplementary-article-runs/column-check-first.log)。

写作过程中还修正了源码路径和截取范围，并以最终Git对象逐段重查。语义修正包括：Agent发布前存在持久追加await；MCP断线不会总是立即撤销旧工具；Schedule具有持久task与恢复机制；业务receipt不同于模型回复；本地授权不等同于企业SSO。正文与图注均采用这些经源码确认的边界。

## 复核命令与范围

准备固定checkout、示例依赖及Pillow环境后，在本研究仓库根目录运行：

```sh
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-supplementary-articles.py
node research/deepseek-harness/validation/check-artifacts.mjs
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-column.py
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-config-startup-article.py
git diff --check
```

本批已执行上述检查，退出码和标准输出保存于[检查日志](supplementary-article-runs)。补充检查器只验证本批，原column与00检查器用于确认既有内容继续有效。

## 实现分析与产品验收的区别

19篇依据现有`replace/mutate`解释恢复继承值，没有创造源码不存在的`reset`接口。21篇以实际`ui-settings-agent-loop`作完整跨端样例，通过现有Client/jsdom与Gateway测试解释链路；没有另建并声称验收一个企业浏览器产品。25篇区分三种独立机制，新增组合方案属于企业应用设计。26、27篇复用真实本地enterprise示例验证授权和幂等，远端连接、vault、SSO与集群映射仍属接入设计。28篇验证的是参考扩展的局部tarball消费，而非完整Harness发行安装。

本批没有执行真实模型服务、真实MCP server、真实SSH host、企业SSO、浏览器E2E、完整Web/Desktop/native构建、干净环境全量Harness安装、跨平台升级迁移或生产部署。协议mock、受控模型、jsdom和脚本fixtures分别证明其契约范围。配套[回归矩阵](../appendices/change-impact-regression-matrix.md)列出了后续产品验收应补充的测试面。
