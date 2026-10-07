# DeepSeek Harness 源码研究与工程实践

面向 Agent 系统开发者与架构师的中文技术研究：从源码还原 DeepSeek Harness 的架构与运行机制，以可复现的 TypeScript 扩展连接原理与工程落地，为专属智能体和私有 AI 工作台提供设计依据。

## 技术价值

- **理解执行机制**：深入 Agent Loop、模型适配、上下文组装、工具调度与状态持久化，追踪正常、失败和取消链路。
- **掌握扩展契约**：分析 Cordis 插件、服务注入、作用域与生命周期，提供自定义工具和模型路由策略示例。
- **支撑企业落地**：以工单助手演示可信身份绑定、授权撤销、持久调用预算、协作取消与 SQLite 幂等事务。
- **结论可追溯、验证可复现**：固定源码 SHA，保留证据、测试与失败记录，明确区分源码事实、运行结果和改造建议。

## 内容导航

| 内容 | 入口 |
| --- | --- |
| 四篇主题报告 | [宏观架构](research/deepseek-harness/01-architecture.md) · [源码运行](research/deepseek-harness/02-runtime-source.md) · [扩展实践](research/deepseek-harness/03-extension-practices.md) · [企业开发](research/deepseek-harness/04-enterprise-harness-practices.md) |
| 29 篇技术专栏与机制图（00—28） | [专栏目录](research/deepseek-harness/articles/README.md) |
| 12 篇二次开发补充专题 | [文档列表与大纲](research/deepseek-harness/appendices/supplementary-article-outlines.md) · [扩展契约矩阵](research/deepseek-harness/appendices/extension-contract-matrix.md) · [回归矩阵](research/deepseek-harness/appendices/change-impact-regression-matrix.md) |
| 可运行的 TypeScript 示例 | [示例与环境准备](research/deepseek-harness/examples/README.md) |
| 源码证据与验证记录 | [证据索引](research/deepseek-harness/appendices/evidence-index.md) · [验证附录](research/deepseek-harness/appendices/validation.md) |
| 源码文章深化技能 | [Source Code Article Refiner](skills/source-code-article-refiner/SKILL.md) |
| 可复用研究与版本同步流程 | [Harness Research Sync](skills/harness-research-sync/SKILL.md) |

建议从宏观架构开始，按需进入源码运行与技术专栏；二次开发可直接阅读扩展实践和示例。

## 基线与验证

研究基于 DeepSeek Harness **`0.2.1-alpha.1`**，固定提交 **`5badb15009ae1756c3afe0ae0cef1faafc290ccc`**，详见[研究基线](research/deepseek-harness/appendices/baseline.md)。已有记录覆盖选定上游契约与自定义扩展，合计 **1,520 个用例通过、1 个条件跳过**。

补充专栏本批另行复核了 **848 项通过、1 项平台条件跳过**，并完成参考扩展的本地 tarball ledger 消费检查；与历史用例存在重叠，不累加统计。范围及失败日志见[本批验证记录](research/deepseek-harness/validation/supplementary-articles-validation.md)。

按示例说明准备固定源码 checkout、依赖及 vendor 声明后，在仓库根目录运行：

```sh
node research/deepseek-harness/validation/enterprise-example.mjs typecheck
node research/deepseek-harness/validation/enterprise-example.mjs build
node research/deepseek-harness/validation/enterprise-example.mjs test
```

示例使用真实 Harness Loop 与受控模型适配器进行本地验证；真实模型服务、企业身份系统及生产部署仍需独立验证。
