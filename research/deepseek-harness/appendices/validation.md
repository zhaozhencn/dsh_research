# 验证范围、复现及结果

历史批次中的文章篇次沿用当时编号；文章链接指向当前文件。最新阅读顺序与原关注点的对应关系见[篇次调整记录](../validation/article-reorder-review.json)。

环境与SHA见[baseline](baseline.md)。所有命令使用固定checkout；新增示例从报告validation脚本进入真实runtime。没有提供模型凭据，没有生产业务系统副作用验证；V13 的业务写入仅发生在真实本地 SQLite 临时数据。JSONL测试采用仓库测试自己的临时数据和mock；POSIX lease用本机native flock。

## 结果与计数口径

原研究 V01—V07 去重后：**22 个仓库测试文件＋1 个自定义测试文件，1,001 个用例通过，1 个条件跳过。** 此后 V08 另运行 7 个不重复的仓库测试文件，201 个用例通过、0 失败或跳过；V10 再运行 6 个不重复仓库文件，302 passed、0 failed/skipped；截至 V12 为 **35 个仓库文件＋1 个自定义文件，1,504 passed、1 conditional skipped**。本轮企业补充 V13 新增 1 个自定义文件、16 passed；当前去重合计 **35 个仓库文件＋2 个自定义文件，1,520 passed、1 conditional skipped**。不是全仓测试，也不是代码覆盖率。

|批次|命令范围|预期|实际／日志|
|---|---|---|---|
|V01核心|8 files：Loop、cancel、tools、request error/reconstruction、scope lifecycle、fork、config reload|离线契约正确|240 passed；[focused](../validation/focused-tests.log)|
|V02子系统初次|11 files：存储3＋SDK＋projection、HMR2、retry、stream2、approval|全部suite能执行|4 failed/7 passed；154 failed/511 passed/1 skipped；原生flock缺失；[原始](../validation/subsystem-tests.log)|
|环境修复|build:native-system|本机Node addon生成|退出0；[native build](../validation/native-build.log)|
|V03复跑|受影响4 files＋timeout-policy|native可用后通过|328 passed/1 skipped；[rerun](../validation/native-rerun-tests.log)|
|V04恢复|resume.spec.ts、repair.spec.ts|重建／补缺与fork边界正确|79 passed；[resume](../validation/resume-tests.log)|
|V05扩展|编译后的两个独立插件，5用例|生效、隔离、异常／取消与清理|5 passed；[examples](../validation/examples-tests.log)|
|V06类型／构建|vendor声明build＋插件及mock严格check＋ESM转译|退出0且保留peer单例|全部退出0；[types](../validation/examples-typecheck.log)、[build](../validation/examples-build.log)|
|V07文稿自查|本地链接、固定source anchors、格式、SHA与Mermaid parse|无缺失引用／错误图|见[artifact-check.json](../validation/artifact-check.json)；本次文稿补充后重新执行|
|V08架构补充|7 files：goal、goal-round-driver、tool-goal、session-telemetry、OTel 2 files、present|新增契约的正常、拒绝、取消与清理路径通过|201 passed、0 failed/skipped；[JSON](../validation/architecture-supplement-tests.json)、[日志](../validation/architecture-supplement-tests.log)、[运行台账](../validation/architecture-supplement-run.json)|

|V10运行关注点补充|6 files：plan、todo、jobs、structured child、workspace、compaction|选定状态提交、取消与错误路径通过|302 passed、0 failed/skipped；[JSON](../validation/runtime-supplement-tests.json)、[日志](../validation/runtime-supplement-tests.log)、[运行台账](../validation/runtime-supplement-run.json)|

去重算法：V02已通过的7完整文件共349 tests；其失败4文件原先仍有162通过，不再与V03叠加。最终240＋349＋328＋79＋5＝1,001。1 skipped是catalog-migration的`isolates invalid compressed child frames`在plaintext参数下不适用；zstd参数有对应执行，不是将失败隐藏为skip。

初次命令还误指定 `timeout.spec.ts`，实际文件为`timeout-policy.spec.ts`；文件不存在不计为已测试，V03纠正并执行。恢复批次还指定不存在的vendor/effect.spec.ts，未被发现，不计为测试；Fiber effect分析属于源码证据而非该虚构测试文件的通过结果。

## 精确复现命令

```sh
cd /Users/zz/prj/dsh_research/.sources/deepseek-harness
corepack pnpm install --frozen-lockfile --ignore-scripts
corepack pnpm run build:native-system
corepack pnpm exec vitest run packages/core/agent-loop/tests/loop.spec.ts packages/core/agent-loop/tests/cancel.spec.ts packages/core/agent-loop/tests/tool-calls.spec.ts packages/core/agent-loop/tests/request-error.spec.ts packages/core/agent-loop/tests/request-reconstruction.spec.ts packages/core/agent-loop/tests/scope-lifecycle.spec.ts packages/core/session/tests/fork.spec.ts packages/boot/app-boot/tests/config-reload.spec.ts --maxWorkers=2
corepack pnpm exec vitest run packages/session/session-projection/tests/registry.spec.ts packages/boot/hmr/tests/reconciliation.spec.ts packages/boot/hmr/tests/profile.spec.ts packages/llm/llm-retry/tests/retry.spec.ts packages/api/session-controller/tests/assistant-stream.host.spec.ts packages/api/session-controller/tests/transport.client.spec.ts packages/interaction/user-approval/tests/approval.spec.ts --maxWorkers=2
corepack pnpm exec vitest run packages/session/session-persistence-jsonl/tests/jsonl.spec.ts packages/session/session-persistence-jsonl/tests/catalog-migration.spec.ts packages/session/session-persistence-jsonl/tests/lease.spec.ts packages/sdk/server/tests/server.spec.ts packages/guard/timeout-policy/tests/timeout-policy.spec.ts --maxWorkers=2
corepack pnpm exec vitest run packages/core/agent-loop/tests/resume.spec.ts packages/core/session/tests/repair.spec.ts --maxWorkers=2
corepack pnpm exec tsc -b vendor/cordis vendor/schemastery
cd /Users/zz/prj/dsh_research
node research/deepseek-harness/validation/check-examples.mjs
node research/deepseek-harness/validation/build-examples.mjs
node research/deepseek-harness/validation/run-examples.mjs
node research/deepseek-harness/validation/check-artifacts.mjs
```

其中7文件命令是对V02完整通过文件的独立复现指令，本研究没有无必要把这些suite重复跑一遍；实际V02原命令还含其余失败文件，日志完整保留。新增scripts接受checkout路径参数；所有工具临时config在finally删除。

## 新增用例：输入与断言不是只镜像注册代码

|输入／条件|要证明的不变量|实际结果|
|---|---|---|
|模型第一Step发research_sum(2,3)，第二Step文本5|canonical工具结果真实进入后续模型请求，Turn闭合|2 requests、2 step/start；第二messages有tool文本5；completed|
|工具参数a='bad'|malformed args不会产出成功结果，Loop仍能接纳错误history|tool/result含INVALID_ARGS；后续Step正常|
|base→挂route(policy)→unload→同Agent再调用→新Agent|listener撤销与durable header状态是两回事|已有Agent retained policy；新Agent base|
|setup中只给Agent A挂route，另建B|Harness Scope确实限制listener|requests按顺序为policy、base|
|stream partial后cancel(user)|等待cancel和结算，保留visible prefix，终止Turn且不重复模型调用|assistant/message存在；turn/end aborted；request数1；whenIdle|

编译输出实际加载进Vitest，运行包都解析到同一checkout源singleton。这里“结算”是Session事件commit；本fixture不挂Persistence，所以并不证明磁盘durability。

## 类型检查与构建边界

初次把整个vendor source透过paths导入严格program，产生vendor既有严格度差异诊断：[initial log](../validation/examples-typecheck-initial.log)。按每个vendor自己的tsconfig先生成声明后，示例、mock严格检查通过：[vendor build](../validation/vendor-type-build.log)、[最终check](../validation/examples-typecheck.log)，空日志意味着退出0且无diagnostics，非漏记结果。

初次tsdown source-alias构建引入运行时副本：[initial build log](../validation/examples-build-initial.log)。最终仅转译插件代码，保持bare package imports，再运行compiled-plugin测试；不在交付中保留vendor源码副本。`transpileModule`本身不做semantic typecheck，因此单列前一个严格类型检查，不能混为一个验证层。

## 本次没有证明的事项

真实模型可用性／流异常网络行为；完整dsh profile启动与发布packed-install；Web/React/Electron E2E与真实网络重连；Linux/Windows confinement；Python runtime wheel；性能、内存增长、跨主机多租户授权；第三方自定义插件的quiescence；外部不可逆副作用回滚。关键正常、错误和取消链均已离线验证，以上边界不会被“单测全部通过”覆盖。

## 此前架构补充的复现与解释（V08／V09）

上游提交保持不变：`5badb15009ae1756c3afe0ae0cef1faafc290ccc`。该次直接更新用户指定的第一篇和公共证据／覆盖／验证材料；没有重新生成另外两篇，也没有执行全仓发布门禁。既有成果沿用 legacy 目录结构，本次新增源码锚点另记录 SHA、Git blob、片段 hash 和局部复核状态，不将目录完整性检查写成新的完整版本研究认证。

```sh
cd /Users/zz/prj/dsh_research/.sources/deepseek-harness
DSH_TELEMETRY_DISABLED=1 corepack pnpm exec vitest run packages/goal/goal/tests/goal.spec.ts packages/goal/goal-round-driver/tests/goal-round-driver.spec.ts packages/goal/tool-goal/tests/tool-goal.spec.ts packages/session/session-telemetry/tests/telemetry.spec.ts packages/session/session-telemetry-otel/tests/otel.spec.ts packages/session/session-telemetry-otel/tests/egress.spec.ts packages/deliverables/tool-present/tests/present.spec.ts --maxWorkers=2 --reporter=json --outputFile=/Users/zz/prj/dsh_research/research/deepseek-harness/validation/architecture-supplement-tests.json > /Users/zz/prj/dsh_research/research/deepseek-harness/validation/architecture-supplement-tests.log 2>&1
cd /Users/zz/prj/dsh_research
node research/deepseek-harness/validation/check-artifacts.mjs
python3 /Users/zz/.codex/skills/harness-research-sync/scripts/research.py check --repo .sources/deepseek-harness --report research/deepseek-harness
node /Users/zz/.codex/skills/harness-research-sync/scripts/check-diagrams.mjs --report research/deepseek-harness --dependencies .sources/deepseek-harness
```

V08 的 JSON 中 `numTotalTestSuites=25` 包含嵌套 describe 分组；按 `testResults` 的文件路径统计才是 **7 个文件**。各文件用例数依次为：goal 35、round-driver 53、tool-goal 23、Session coordinator 34、OTel 42、egress 4、present 10，合计 201。所有 assertion 均 passed。原研究的 1,001 个成功用例没有重跑或重复累计。

新增验证使用仓库自己的测试及临时资源，模型／传输边界受控；未连接真实模型或线上 OTLP collector。MCP 记忆、jobs、规划模式、子 Agent 结构化输出和 workspace changes 的新增分析主要依据源码与官方说明，不冒称该批次已独立运行其完整测试。Mermaid 只做实际 parser 校验，不声称完成视觉渲染或浏览器 E2E。

文稿检查采用 legacy 结构校验（`final_mode=false`），核对了 119 条证据记录与 341 个工作区成员；另以实际 Mermaid 11.16.0 parser 解析三篇报告共 11 张图，全部通过。链接检查针对本地文件与固定 checkout 的源码行号，不证明 GitHub HTTP 可用性。检查输出分别保存在[结构结果](../validation/architecture-supplement-structure.json)、[图表结果](../validation/architecture-supplement-diagrams.json)、[完整材料结果](../validation/artifact-check.json)与[检查日志](../validation/architecture-supplement-artifacts.log)。执行者另核对了 16 项正文与其局部源码的语义对应；机器检查本身不认证架构结论。


## 本次运行关注点补充（V10／V11）

仍使用同一 SHA，直接完善用户指定的第二篇及公共证据、覆盖和验证材料，未修改第一篇／第三篇或上游源码。新增 29 条选段证据（E120—E148），记录 SHA、blob 和片段 hash。沿用 legacy 目录，结构检查使用普通模式，不冒充新版本研究的 final 认证。

```sh
cd /Users/zz/prj/dsh_research/.sources/deepseek-harness
DSH_TELEMETRY_DISABLED=1 corepack pnpm exec vitest run packages/plan/plan-mode/tests/plan-mode.spec.ts packages/todo/tool-todo/tests/integration.spec.ts packages/jobs/jobs-local/tests/jobs.spec.ts packages/subagent/subagent-in-process-driver/tests/structured.spec.ts packages/deliverables/workspace-changes/tests/plugin.spec.ts packages/compaction/compaction-basic/tests/compaction-basic.spec.ts --maxWorkers=2 --reporter=json --outputFile=/Users/zz/prj/dsh_research/research/deepseek-harness/validation/runtime-supplement-tests.json > /Users/zz/prj/dsh_research/research/deepseek-harness/validation/runtime-supplement-tests.log 2>&1
cd /Users/zz/prj/dsh_research
python3 /Users/zz/.codex/skills/harness-research-sync/scripts/research.py check --repo .sources/deepseek-harness --report research/deepseek-harness
node /Users/zz/.codex/skills/harness-research-sync/scripts/check-diagrams.mjs --report research/deepseek-harness --dependencies .sources/deepseek-harness
node research/deepseek-harness/validation/check-artifacts.mjs
```

V10 按 `testResults` 的文件路径和 assertionResults 计数：plan 66、todo 2、jobs 83、structured 30、workspace 16、compaction 105，合计 302；退出状态 0，所有断言 passed，无 fail／skip。6 个文件与此前批次不重复。原有 1,202 成功用例未重跑，累计仅增加本批实际执行结果。

验证层次各不相同：plan 使用真实服务及受控 Agent／准入边界；todo 使用真实 Loop 与 mock 模型；jobs 使用真实本地 registry 和受控生产者；structured 使用真实 Loop／in-process child 与受控模型，部分 PTC 服务为替身；workspace 使用临时仓库和真实本地 Git／subprocess；compaction 使用真实 Session／压缩服务及受控摘要调用。测试并未连接真实模型、外部 MCP memory 或线上遥测 collector，没有完成全产品端到端验证。

V11 已核对 16 项标题与第一篇完全一致、148 个证据锚点及 341 个成员清单；实际 Mermaid 11.16.0 parser 解析三篇共 14 张图（第二篇 7 张），全部通过。本地链接与源码行号检查不证明在线 URL 可达；机器结构检查不认证架构结论，运行描述另经逐段语义复核。

最终检查材料：[结构结果](../validation/runtime-supplement-structure.json)、[图表结果](../validation/runtime-supplement-diagrams.json)、[完整结果](../validation/artifact-check.json)、[检查日志](../validation/runtime-supplement-artifacts.log)。前次 V09 的独立输出保留历史结果，公共 artifact-check.json 反映当前文稿。


## 16 篇技术专栏的文稿验证（V12）

本轮在同一 SHA 上新增 articles 目录：16 篇独立 Markdown、导航、16 张 PNG 与同名 SVG，以及图示数据和验证清单。代码摘录均来自固定 Git 对象，或 V05 已运行的研究测试；没有修改上游 tracked 文件，没有切换版本，没有新增或重复累计行为测试。原运行去重计数仍为 36 文件、1,504 passed、1 条条件 skip。

源码重查发现旧 E147 的反馈授权说明指向了通用 coordinator，而实际 isFeedback 在 session-telemetry-otel 的 index.ts:45–53。本轮校正 E147 的路径、区间、blob、hash 和第二篇对应链接；另外新增 E149，说明交接游标是按 Session 对象保存的模块级 WeakMap。该纠正是语义复核所得，旧结构检查通过只说明路径可定位，不能证明路径支持原说明。

本机在独立 .sources/column-work/.venv 安装 Pillow 11.3.0，用标准绘图生成图示，不调用图像生成模型。PNG／SVG 使用同一节点与文字定义，图片宽 1200 像素，中文字体为系统 STHeiti Medium；生成时检查文字宽度，交付检查读取 PNG 和 SVG，执行者另看总览及代表单图。没有在公众号编辑器里发布或预览。

```sh
cd /Users/zz/prj/dsh_research
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/build-column-assets.py
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-column.py
python3 /Users/zz/.codex/skills/harness-research-sync/scripts/research.py check --repo .sources/deepseek-harness --report research/deepseek-harness
node /Users/zz/.codex/skills/harness-research-sync/scripts/check-diagrams.mjs --report research/deepseek-harness --dependencies .sources/deepseek-harness
node research/deepseek-harness/validation/check-artifacts.mjs
```

专栏检查对照 16 项原目录，核验 33 段代码的原文、缩进与 hash，检查正文源码 SHA／行号、导航及图片链接、代码围栏、PNG 解码／尺寸和 SVG XML／尺寸。源码摘录不是独立程序，未对片段进行新的类型检查，也未声称本轮运行了业务代码。编辑关键词仅验证取舍与心得栏目存在，其内容与图示语义由执行者逐篇复核。

检查材料：[专栏结果](../validation/column-check.json)、[检查日志](../validation/column-check.log)、[摘录与篇章清单](../validation/column-manifest.json)、[legacy 结构结果](../validation/column-structure.json)、[Mermaid 结果](../validation/column-mermaid.json)、[完整材料结果](../validation/artifact-check.json)和[完整检查日志](../validation/column-artifacts.log)。全套证据现为 149 条，工作区成员仍为 341；三篇原报告中的 14 张 Mermaid 使用实际 parser 解析，专栏图示则是已渲染的 SVG／PNG，不将两类图的检查混为一谈。


## 企业专属 Harness 补充（V13／V14）

上游 SHA 不变。本轮新增[企业实践分析](../04-enterprise-harness-practices.md)与[企业工单参考实现](../examples/enterprise-harness/README.md)，保留三篇原报告及 16 篇专栏。企业方案按两篇原文的 16 项关注点展开；新增应用账本不是 DSH SessionPersistence 的替代实现。

V13 对五个 TypeScript 模块和既有真实 runtime fixture 执行严格类型检查，并转译为五个保留 peer imports 的 ESM 模块。测试加载编译后的代码，实际使用 Cordis、Session、Projection、LLM、Tools 和 Loop；模型流由可控 adapter 提供，业务端为真实本地 SQLite。最终一个新增自定义文件有 **16 passed、0 failed/skipped**；旧测试未重跑、未重复计数。当前合计 37 个去重文件、1,520 passed、1 个既有条件 skip。

用例包括完整两 Step 的工具回流与路由、同编号跨 tenant 读取、伪造主体／参数、资源授权、scoped 工具 guard、await 期间撤销、预算耗尽与同 Step 重试、流取消／deadline、Handle 清理、同机两 SQLite 连接与文件重开，以及业务写入／回执／审计共同提交。业务事务用例在真实数据库中注入 audit INSERT 失败，验证已经执行的 UPDATE 与回执 INSERT 一起回滚，再恢复数据库并验证重复调用只有一次效果。

初次 15 个用例中有 11 failed、4 passed，错误来自示例把 raw JSON Schema 的 required 数组混入 defineTool author DSL；这是新增示例的编写错误，不归为上游缺陷。修正为属性级 required 后 15 passed，再增加有界重试场景达到 16 passed；随后扩充既有事务用例进行真实 SQL 故障注入，仍为 16 个去重用例。保留[初次失败日志](../validation/enterprise-tests-initial.log)、[初次 JSON](../validation/enterprise-tests-initial.json)、[修正 patch](../validation/enterprise-schema-fix.patch)、[最终日志](../validation/enterprise-tests.log)、[最终 JSON](../validation/enterprise-tests.json)与[运行台账](../validation/enterprise-runs.json)。类型日志为空的零退出状态另记录于台账。

```sh
node research/deepseek-harness/validation/enterprise-example.mjs typecheck
node research/deepseek-harness/validation/enterprise-example.mjs build
node research/deepseek-harness/validation/enterprise-example.mjs test
python3 research/deepseek-harness/validation/check-enterprise.py
python3 /Users/zz/.codex/skills/harness-research-sync/scripts/research.py check --repo .sources/deepseek-harness --report research/deepseek-harness
node research/deepseek-harness/validation/check-artifacts.mjs
```

V14 检查 16 项映射顺序、16 个测试身份去重、15 条补充源码锚点的 Git 对象片段 hash、示例文件 hash、日志存在、ESM 相对依赖／peer 声明和干净 checkout；完整文稿检查另验证本地链接、固定 SHA／区间及 Mermaid parser。结构脚本沿用现有 legacy 模式（final_mode=false），没有伪造新的 research-state 或把同版本补充称为完整版本同步认证。当前文档共有原报告的 14 张 Mermaid 加企业实践的 2 张，实际 parser 全部通过；检查不包含渲染或 HTTP 全量访问。

检查输出：[企业材料结果](../validation/enterprise-check.json)、[legacy 结构结果](../validation/enterprise-structure.json)、[完整材料结果](../validation/artifact-check.json)、[检查日志](../validation/enterprise-artifacts.log)；[补充源码锚点](../validation/enterprise-source-anchors.json)独立保存，不改变原 E01—E149 台账。

本轮未验证 SSO、企业实际权限服务、真实模型、远端业务幂等协议、Vault、完整 profile、packed install、UI、持久 DSH Session 联调、跨机队列／数据库、真实多租户部署或性能。SQLite 的两连接／文件重开不等于集群并发，Loop attempt 预留次数不等于货币计费；最终 observer 的审计仍不提供强持久完成屏障。以上限制均在正文和代码说明标明。


## 第一篇专栏深化：逐段源码解读

本次仅深化[第 01 篇](../articles/15-task-completion.md)，上游 SHA 不变，原有七个主体章节、机制图与篇章导航保留，其余 15 篇正文没有改写。第一篇从 2 段源码增至 23 段，按 13 个执行步骤解释目标创建、revision 比较更新、自动调度、输入接纳、检查点、取消与状态发布；另外分析 Loop 结束、结构化子任务、todo、规划模式和业务验收的区别。源码摘录清单当前合计 54 段；原专栏的 33 段计数保留为历史批次结果。

专栏检查重新读取固定 Git 提交的原文，核对摘录内容、区间、hash、16 项映射、链接与 PNG／SVG；另核对七个主体标题和原图未变化、其余 15 篇正文与当前已提交原文一致。既有 V08 的七个相关测试断言逐项与 JSON 结果对照，均为此前已执行的 passed；没有新增或重跑行为测试，累计测试数保持 1,520 passed、1 conditional skipped。

最初使用系统 Python 运行文稿检查时缺少 Pillow，退出 1；随后使用已准备的专栏虚拟环境运行，退出 0。保留[初次环境失败](../validation/first-article-check-initial.log)、[专栏检查日志](../validation/first-article-check.log)、[本轮复核记录](../validation/first-article-review.json)、[首次完整材料检查](../validation/first-article-artifacts-initial.log)及[最终完整材料检查](../validation/first-article-artifacts.log)。首次完整材料检查还发现复核记录链接先于文件生成；补齐记录后再检查。上述失败均保留。这些检查验证文稿与证据一致性，不证明新的业务行为、类型编译或真实模型修复结果。

```sh
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-column.py
node research/deepseek-harness/validation/check-artifacts.mjs
```

使用既有本地虚拟环境是本次工作区的复现方式；其他环境需先安装 Pillow。记录另外说明工作区已有研究 README 删除，本轮保留该改动；文稿检查按当前实际文件执行，不恢复或改写用户的删除。

## 全系列深化与插图补充

本次沿第一篇的分析逻辑，深化第02—16篇，保留全部16篇原有主体标题、段落、原文代码及导航；第一篇正文论证保留，额外补充插图。源码仍固定为`5badb15009ae1756c3afe0ae0cef1faafc290ccc`，未更新checkout。新增内容沿定义、provider、consumer、执行、提交、异常与清理展开，解释关键条件和等待窗口，并区分源码事实与企业改造建议。

当前专栏共有**298段原文代码摘录**，各篇分别为23、20、18、17、19、21、16、20、18、19、18、17、16、18、20、18段。历史批次的33段和54段保留为当时结果。每篇新增3张插图，连同原图各4张，合计**64张PNG及64张SVG**；原16组图片与编辑基线`d4b60a4`逐字节相同。新增48组图分别解释执行步骤、状态/数据归属和关键条件分支，宽1200像素，共用PNG/SVG几何定义。

[专栏检查脚本](../validation/check-column.py)增加原有章节保留、每篇4图、图示映射与摘录引用检查，并读取固定Git原文核对代码、行号、hash、文稿映射、链接和图片结构。[结构基线](../validation/column-structure-baseline.json)保留原章节。单一执行者另核对原段落保留，查看48张新增PNG的三组总览和代表性单图，调整长英文标识断行；图示语义依据正文源码分析复核。结构与关键词检查本身不认证架构结论，SVG仅检查XML、尺寸及共享绘图几何，未进行独立浏览器渲染。

```sh
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/build-column-assets.py
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-column.py
node research/deepseek-harness/validation/check-artifacts.mjs
git diff --check
```

绘图入口先生成原图，再调用[补充渲染器](../validation/build-column-supplements.py)，从[新增图定义](../articles/assets/diagram-supplements.json)重建48组插图并合并清单。使用本地Pillow虚拟环境；其他平台须安装Pillow，并通过`DSH_COLUMN_FONT`提供中文字体。[重建日志](../validation/series-diagrams-rebuild.log)记录完整入口成功，正文检查与完整材料检查最终输出分别见[专栏日志](../validation/series-deepening-column.log)、[材料日志](../validation/series-deepening-artifacts.log)、[专栏结果](../validation/column-check.json)及[材料结果](../validation/artifact-check.json)。

渲染首轮成功，改进英文断行时先触发纵向边界断言，再发现长标识超过最小字体宽度；修正边界检查并改用中文图中标签后全部重建成功。预算归集图另改为调用树，避免暗示摘要与子任务必须按固定顺序运行，该图首次渲染的断言把末行间距计入可见文本高度，修正后重建成功；保留[调用树边界失败](../validation/series-diagrams-call-tree-failure.log)和[最终绘图日志](../validation/series-diagrams-final.log)。保留[初次渲染](../validation/series-diagrams-initial.log)、[断行边界失败](../validation/series-diagrams-wrap-failure.log)、[长标识失败](../validation/series-diagrams-identifier-failure.log)与[修正渲染](../validation/series-diagrams-corrected.log)。正文检查首轮通过；完整材料检查首轮发现目录引用的复核JSON尚未创建，补齐后再次检查，保留[初次正文日志](../validation/series-deepening-column-initial.log)和[初次材料失败](../validation/series-deepening-artifacts-initial.log)。这些是文稿制作与排版问题，不是runtime测试失败。

[复核记录](../validation/series-deepening-review.json)汇总逐篇数量、结构保留、原图一致性、命令、修正与限制。本次**没有新增或重跑行为测试**，沿用此前同一SHA的37个去重文件、1,520 passed、1条条件skip；没有新增类型编译、真实模型、生产多租户、跨平台或在线升级验证。Markdown与图片为本地交付，未在公众号编辑器预览或发布；研究README既有删除保持不变。

## 第02篇叙事修订：整体架构、连续调用与术语

按阅读反馈重写[第02篇](../articles/03-agent-loop.md)，保留七个主体关注领域，调整标题和展开顺序。正文先交代组件分工和 Turn／Step／attempt，随后用14个连续步骤追踪创建、输入、driver、准入、请求、stream、工具回流、结束、重试、取消与释放。每次进入内部函数先交代调用现场，离开时解释返回值和下一站；29段源码均来自原固定提交。全系列当前为307段，历史深化批次的298段仍保留为当时结果。

四张PNG及SVG重新绘制，按整体主线、循环嵌套、数据提交边界、异常路径顺序嵌入；第三张移至请求构造之后，衔接后面的stream与工具回流。单一执行者查看全部四张PNG并复核图示语义；检查新增第02篇的图序、所在主体章节和 Agent／Turn 英文术语约束。保留原[结构基线](../validation/column-structure-baseline.json)与历史深化复核，另用[编辑修订约定](../validation/column-editorial-revisions.json)记录本篇的新旧标题和图片位置，不把历史“原章节保留”结论改写为本轮结果。

```sh
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/build-column-assets.py
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-column.py
node research/deepseek-harness/validation/check-artifacts.mjs
git diff --check
```

[本轮复核记录](../validation/agent-loop-review.json)记录修改前本仓库提交、文稿hash、范围与命令。其他15篇正文及其120个PNG／SVG文件逐字节对照该编辑基线未变；上游仍为原SHA，checkout未修改。未新增或重跑runtime测试和类型编译，既有37个去重文件、1,520 passed与1条条件skip仅作为历史证据。

初次绘图发现数据边界图标签超出纵向边框，缩短标签后重建成功；保留[首次绘图失败](../validation/agent-loop-diagrams-initial.log)、[修正绘图](../validation/agent-loop-diagrams.log)和[最终重建](../validation/agent-loop-diagrams-final.log)。之后图片位置元数据调整，第一次正文检查指出图清单尚未重建，保留[初次正文检查](../validation/agent-loop-column-initial.log)；重建后再次执行检查。最终结果见[正文日志](../validation/agent-loop-column.log)、[完整材料日志](../validation/agent-loop-artifacts.log)、[差异检查日志](../validation/agent-loop-diff-check.log)、[专栏结果](../validation/column-check.json)和[材料结果](../validation/artifact-check.json)。检查验证源码可定位性、结构和资产一致性，不认证业务正确性；未在公众号编辑器预览或发布。

## 第02篇进一步优化：步骤衔接、核心数据与务实心得

继续完善[第02篇](../articles/03-agent-loop.md)，七个主体标题、14个步骤标题和此前29段原文摘录保留。在章节及关键步骤之间补充上一阶段的数据、下一阶段的消费方与修复任务场景；新增9段结构及状态代码，解释 Phase、InboxState、PreparedStep、PromptAssembly、LlmCallConfig、PreparedLlmCall、AssistantStreamAttempt，以及工具调度的 PlannedCall、Slot、GroupOutcome 和游标。当前本篇38段，全系列316段；此前307段仍是上一批次结果。

同时澄清 Inbox 的持久 projection 与模型可见 user/message 的区别，区分 config 数据、preparedCall 调用能力与最终 request 字段，并通过 slots／committed 的具体例子说明并发返回和有序提交。结尾改为与正文对应的四项实践收获，保留实现边界，将适用的设计经验落到恢复、观察、验收与退出。四张图保留原阅读位置，改用 Inbox、request、live stream、tool runtime 与源码类型标识；逐张查看PNG，并复核 request.messages 的来源和 retry 获准条件。

```sh
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/build-column-assets.py
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-column.py
node research/deepseek-harness/validation/check-artifacts.mjs
git diff --check
```

[本轮复核](../validation/agent-loop-refinement-review.json)记录编辑前提交、保留结构、新增摘录位置与hash、实际命令和限制。对照编辑基线，其他15篇正文及120个PNG／SVG文件未变；上游SHA与checkout保持原状。初次渲染通过，语义复核后明确 running Phase、request.messages 与获准 retry，再次完整重建；保留[初次绘图](../validation/agent-loop-refinement-diagrams-initial.log)和[最终绘图](../validation/agent-loop-refinement-diagrams.log)。最终检查记录见[正文日志](../validation/agent-loop-refinement-column.log)、[完整材料日志](../validation/agent-loop-refinement-artifacts.log)、[差异检查](../validation/agent-loop-refinement-diff-check.log)、[专栏结果](../validation/column-check.json)及[材料结果](../validation/artifact-check.json)。

本轮没有新增或重跑runtime测试及类型编译，不改变历史测试统计。文稿和图示检查验证原文、定位、结构及资产一致性；语义另由单一执行者复核，没有真实模型任务、公众号编辑器预览或发布，也没有独立SVG浏览器渲染。

## 其余15篇同步完善：衔接、核心数据与图文组织

本次按第02篇的优化标准修改第01、03—16篇，源码仍固定为`5badb15009ae1756c3afe0ae0cef1faafc290ccc`。各篇补充开头的整体说明，以前一阶段输出、caller／callee、交接数据与返回决定连接步骤；不同生命周期和独立分支明确标出切换位置。关键步骤新增48段核心数据与状态原文，配合字段、用途和消费位置解读，全系列现有364段摘录。结尾分别提炼与正文对应的实践收获，具体实现边界仍保留在分析中。

15篇保留各自主体章节数量、原步骤顺序及所有既有摘录，标题按英文术语与心得主题作必要调整。四张图依正文关注点重新分布，60张PNG和60张SVG重绘，保留Agent、Turn、Step、attempt及源码标识；调用时序、并列数据对象和成本关联分别表达。第02篇正文与其8个PNG／SVG文件对照编辑基线逐字节未变。历史结构基线和验证批次不改写；新旧标题及图片位置由[现行编辑约定](../validation/column-editorial-revisions.json)明确记录。

```sh
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/build-column-assets.py
.sources/column-work/.venv/bin/python research/deepseek-harness/validation/check-column.py
node research/deepseek-harness/validation/check-artifacts.mjs
git diff --check
```

[逐篇复核记录](../validation/series-refinement-review.json)保存编辑前提交、文稿hash、新增结构与固定SHA原文范围、保留检查、图片分布和实际命令。单一执行者复核字段与caller、consumer的关系，查看四组图片总览，特别检查文件写入与进程confinement分路、prepared registration的闭包归属、scheduler真实方法、结构化capture的最终结算及预算图的成本关联。绘图脚本从同一几何定义生成PNG／SVG，并检查文字宽度与纵向边界。

本轮编辑辅助脚本首次解析出现UTF-8编码声明问题，保留[初次制作日志](../validation/series-refinement-authoring-initial.log)，显式声明编码后生成成功；这是文稿制作问题，不是runtime失败。[首次重建](../validation/series-refinement-diagrams-initial.log)通过，语义复核后修正部分源码标签与衔接文案，再[完整重建](../validation/series-refinement-diagrams.log)。[首次正文检查](../validation/series-refinement-column-initial.log)通过；最终输出见[正文日志](../validation/series-refinement-column.log)、[完整材料日志](../validation/series-refinement-artifacts.log)、[差异检查](../validation/series-refinement-diff-check.log)、[专栏结果](../validation/column-check.json)和[材料结果](../validation/artifact-check.json)。

没有新增或重跑runtime测试、类型编译、真实模型或部署实验。此前同一SHA的37个去重测试文件、1520 passed、1个条件skip保留为历史证据。文稿检查证明原文、定位、结构及资产一致性，语义判断另行复核；未在公众号编辑器预览或发布，未进行独立SVG浏览器渲染，上游checkout保持原SHA且无改动。


## 专栏阅读顺序调整：扩展性优先

先交换原第01与第14篇，再把原第16篇移到第02篇。当前顺序对应原篇次为：14、16、02、03、04、05、06、07、08、09、10、11、12、13、01、15。插件扩展与生命周期位于开篇，部署与版本演进紧接其后；原研究报告的16项编号保持不变，以独立 concern_number 记录文章与关注点的对应关系。

本次同步文章及图像文件名、篇次标识、篇间导航、当前目录与清单；历史摘录ID、结构基线、复核JSON和日志保留原编号。全部364段原文摘录及主体标题与编辑前一致，64组PNG／SVG仅更新对应篇次，图示机制定义保留。绘图入口按原关注点选取机制，材料检查按显式对应关系核验，避免将阅读顺序误认为原报告编号。

专栏检查与完整材料检查退出0，结果分别见[专栏日志](../validation/article-reorder-column.log)、[材料日志](../validation/article-reorder-artifacts.log)和[调整记录](../validation/article-reorder-review.json)。查看了新顺序的16图总览。本次未新增或重跑类型、构建及runtime行为测试，没有切换上游SHA，也没有执行外部发布。
