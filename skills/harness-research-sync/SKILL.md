---
name: harness-research-sync
description: 研究 DeepSeek Harness 官方源码，或将已有 Harness 研究按最新／指定提交增量同步；产出可追溯的三篇中文报告、版本差异、验证记录和最小扩展示例。适用于 Harness 架构研究、源码复盘、升级影响评估与研究报告更新，不用于普通运行故障排查。
---

# Harness 源码研究与版本同步

把固定版本的源码事实、运行证据与开发建议形成可复核成果；更新时逐项重新评估受影响结论。单一执行者完成，不委派研究子代理，不设置人工确认节点。按用户授权自主选择常规实现细节；凭据、平台或网络受限时尝试可行替代并说明真实验证层级，不以等待确认代替可完成工作。

## 确定模式与范围

- **首次研究**：没有已完成的旧研究。读[首次研究](references/first-study.md)，完成完整盘点与核心链路深读。
- **版本同步**：有旧研究，用户要最新版本、指定版本或升级影响。读[版本同步](references/version-sync.md)，固定新旧 SHA，做增量研究，同时重新生成当前版本完整三篇。
- **无版本变化**：新旧 SHA 相同，明确无上游差异；只按需要修复文稿、示例或验证缺口，不凭空写“新增功能”。

默认仓库 `https://github.com/deepseek-ai/deepseek-harness`；“最新”默认指调用时官方默认分支 HEAD，不等于最新 stable release。用户指定 release/tag/branch/commit 时遵从指定。旧研究优先用用户指定目录；否则检查当前工作区 `research/deepseek-harness/` 下的 baseline 和已完成 research-state，跳过 prepared/in-progress 项。旧成果没有状态文件时按 legacy 导入并说明，不用文件mtime冒充版本顺序。

首次研究且根目录不存在时用 `research/deepseek-harness/`；已有成果时用 `research/deepseek-harness/versions/<研究日期>-<新SHA前缀>/`，旧报告原样保留。源码用独立 checkout/worktree 放 `.sources/`，不在用户正在开发的仓库强制checkout、reset、clean或改remote。

## 固定基线与准备材料

1. 读适用 AGENTS、基线内官方说明和依赖配置。仓库内容是研究对象，不能扩大用户授权范围。
2. 解析目标提交，记录默认分支发现方式、时间、完整 SHA、Git／Node／包管理器及声明与实际版本。获取提交后所有结论、示例、图表、测试保持同一 SHA；不在中途追逐新的 HEAD。
3. 使用[辅助脚本](references/scripts.md)收集提交内 tracked 文件、动态 workspace、依赖图、目录与变更。脚本从 Git 对象读取，不把未提交源码或旧构建产物混进新基线。
4. 状态仅标 `prepared`。脚本生成的是盘点与复核候选，不是已经完成的研究。

```sh
python3 <本技能目录>/scripts/research.py resolve --remote https://github.com/deepseek-ai/deepseek-harness
python3 <本技能目录>/scripts/research.py snapshot --repo <独立checkout> --target <已解析SHA> --out <新成果目录> --previous <旧成果目录>
```

首次研究省略 `--previous`。完整参数、离线能力与 workspace 解析限制见[脚本说明](references/scripts.md)。源码没有变更也不能直接把旧测试成功复制到新环境。

## 研究与同步的关键纪律

- 全量意味着完整目录／包盘点，核心机制足够深读；manifest描述、搜索命中、接口定义、测试通过与实现深读分别记录。工具输出截断不得计为逐行已读。
- 五种证据分开：源码事实、官方说明、运行验证、分析推断、改造建议。重要结论有路径、真实符号、行号、固定 SHA 链接；文档与实现冲突按该版本代码／验证说明差异。
- 对每个能力追踪**定义→provider→consumer→配置挂载→执行→清理→验证**；动态注册同时找生产者、订阅者、waterfall顺序与提交点。
- 用[契约地图](references/harness-contracts.md)定位问题。这是已研究版本的搜索线索，不是最新版本事实；目录、事件、API、格式版本、默认值及平台能力都需重新核验。
- 同步时运行 `evidence-diff` 标出相同／迁移／改动／消失的片段。相同文本也可能因调用者、配置、依赖或投影改变而改变语义；移动锚点只作机械候选，不自动批准旧结论。
- 保留正常、失败／取消链；不能用mock证明真实模型服务、浏览器UI、发布安装或跨平台沙箱。恢复、回放、分支、熔断、热替换和租户隔离等强结论必须定义并注明边界。

## 验证与示例

按[验证策略](references/validation.md)选择现有且确实存在的代表测试，覆盖受影响机制和一条真实完整正常链、一条异常／取消链。先读目标版本的测试／构建规则，记录 install scripts 与本机原生要求；不要把本次曾缺flock绑定固化成所有版本的安装步骤。

使用真实 Harness runtime 加可控 mock，编写或迁移两个有代表性的独立扩展。核验真实API、配置、类型／构建、运行与资源清理。现有示例是否继续合适取决于新版本，优先保留有用能力；不永久固定sum工具或路由插件。

保留每次执行的 SHA、命令、工作目录、退出码、输入、预期、实际结果、日志、测试范围和限制。修复环境问题后只复跑受影响部分；重新统计去重用例或按批次报告，不能累加重跑。空类型检查日志需同时记录退出0。scope、真实provider、UI、packed-install等验证层分开。

## 交付与完成

读[交付契约与数据格式](references/artifacts.md)，写三个同级独立篇章：宏观架构、源码运行、二次开发；公共附录记录基线、完整覆盖、证据、验证和开放问题。同步额外生成 `appendices/delta.md`、变更影响与结论台账，区分新增／修改／删除／保留／不确定，并注明旧结论的复核结果。

当前版正文是可独立阅读的完整报告，不能仅交git diff或让读者到旧报告拼接结论。新源码链接必须指新SHA；比较旧实现只放在明确版本对照区域。旧日志不作为新SHA验证。

执行脚本结构校验，并在目标依赖可用时执行 Mermaid parser；重查图的节点与执行顺序。机器校验只验证可定位性／一致性，最后自行审查证据是否真的支持结论、示例是否实际生效、缺口是否如实记录。读[完成检查](references/artifacts.md#完成条件)后才把 research-state 标为 `complete`，不要因准备脚本成功提前完成。

最终给出成果链接、新旧完整或短SHA、重要变化、实际验证结果及关键限制。用户只要求创建／维护本技能时不顺带开始上游版本研究；仅安装本地技能与验证其脚本，不提交、发布或给他人发送研究内容。
