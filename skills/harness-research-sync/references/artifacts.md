# 交付契约与数据格式

## 目录与正文

首次成果且根目录不存在时直接使用 `research/deepseek-harness/`；已有成果的版本同步采用以下目录。用户指定位置优先。

```text
research/deepseek-harness/versions/<日期>-<SHA前缀>/
  research-state.json
  README.md
  01-architecture.md
  02-runtime-source.md
  03-extension-practices.md
  appendices/
    baseline.md / baseline.json
    coverage.md / coverage.json
    evidence-index.md / evidence.json
    validation.md
    open-questions.md
    workspace-inventory.json / dependency-graph.json
    tracked-files.json / tracked-files.txt / directory-inventory.json
    delta.md / claims.json                # 有旧版的同步
    changes.json / impact.json / commits.json / evidence-status.json
  examples/<独立示例>/
    index.ts 或入口文件 / package.json / README.md / 配置
  validation/
    runs.json / logs/ / 必要复现和 mock
```

三个正文同级独立，共用证据附录。README 包含基线、导航、主要结论、完成范围与限制。第一篇讲组成与边界，第二篇讲执行与状态，第三篇讲契约、示例与定制。同步不是第四篇；delta 为公共附录。

baseline 由 snapshot 生成，补锁文件解析版本、实际使用工具、在线资料访问日期和版本关系；不同来源分别标注。coverage.json 与 workspace-inventory 路径集合一致，每个包补职责、read_paths、depth、verification、chapters、open、reviewed_at_sha。顶层非包目录在 coverage.md 另表记录，包括 vendor/生成代码的范围与排除理由。

## 证据格式

evidence.json 是编号→记录的对象。编号稳定但记录随版本重新复核，不能把旧引用偷偷挂到新 SHA。通用字段：category（五类之一）、sha（当前完整 SHA）、symbol／claim、review_status=reviewed、适用条件和限制。

源码事实与基线内官方说明使用 path/start/end；建议同时写 blob_id 和 snippet_hash。snippet_hash 为 Git blob 按 splitlines 截取该区间、以单个换行连接后 UTF-8 SHA256，不含末尾额外换行。固定链接可按 repository/blob/SHA/path#Lx-Ly 生成，URL编码路径。

```json
{
  "E01": {
    "category": "源码事实", "sha": "<当前完整SHA>",
    "path": "<真实文件>", "start": 1, "end": 4,
    "symbol": "<真实符号>", "claim": "<结论与条件>",
    "review_status": "reviewed", "snippet_hash": "<片段SHA256>"
  },
  "R01": {
    "category": "运行验证", "sha": "<当前完整SHA>",
    "run_ids": ["run-normal-1"], "claim": "<受测范围结论>",
    "review_status": "reviewed"
  },
  "A01": {
    "category": "分析推断", "sha": "<当前完整SHA>",
    "based_on": ["E01", "R01"], "premise": "<前提与不确定性>",
    "claim": "<条件成立时的推断>", "review_status": "reviewed"
  }
}
```

运行验证对应本次 runs.json；推断和改造建议用 based_on 引用其他证据，加 premise，不允许把循环引用当独立事实。外部官方资料与相关提交在 evidence-index.md 记录完整URL、访问日、版本及性质，不能用无来源文句代替源码／运行依据。

evidence-status.json 是机械定位候选，所有记录 pending；它不是 evidence.json。缺失或改动不能自动说明能力被删；相同片段也不说明行为未变。无法复核项写 open-questions，并降低／删除正文强断言；不把未解决项填 reviewed。

## 结论与运行台账

claims.json 为数组；每项包含 id、old_claim、current_claim、status（new/modified/retained/removed/uncertain）、reason、evidence_ids、reviewed_at_sha。非 uncertain 项需要新证据，uncertain 明确影响与下一步。删除项用目标版替代实现和差异解释；旧SHA证据只在 delta 比较区出现。

运行台账格式见 validation.md。日志相对路径以成果根目录为基准。命令、输入、预期、实际、失败／阻碍、退出码与环境全部可复核，凭据脱敏。旧测试日志不进入本次已运行的台账。

## 完成条件

完成前逐项自查：

1. 三篇完整，scope 覆盖原任务，核心机制与必要依赖已真实深读；包覆盖和非包范围如实区分。
2. 结论、源码、图表、示例和运行记录使用同一固定 SHA；声明／lock／实际环境区分。
3. 五类重要结论可定位；文档与实现差异、否定性结论范围、推断前提准确。
4. 正常和失败／取消链有真实符号、状态、事件、提交点；可运行关键链已验证，不能运行的限制已明示并降级表述。
5. 所有图已实际语法解析并核对语义；链接、证据编号、依赖和相对文件可定位。
6. 替换矩阵、作用域、清理、生效方式、接口稳定性及两个独立示例完整，构建／运行程度分别记录。
7. 私有化／多用户／多 Agent 方案区分原生与新增工程，没有虚构产品保证或人日／性能数据。
8. 同步的影响分析、claim 分类、当前完整报告与示例迁移完成；无差异如实说明。
9. --final 的机器检查通过，且执行者完成语义自查。记录 checks 的命令、结果与日志。

只有可完成工作全部完成且限制清楚，才写 state.status=complete、completed_at、checks、limitations 和 assurance（verified 或 limited）。complete 表示本轮交付完成，不代表全功能／全平台已验证。关键环境阻碍仍在时 assurance=limited，并在 README/validation/open-questions 中说明；尚有可继续完成的必需工作时保持 in-progress。prepared 绝不算完整研究。

最终响应给新旧SHA、可点击报告、实际验证范围和重要限制，不用“全面吃透”等措辞代替证据。
