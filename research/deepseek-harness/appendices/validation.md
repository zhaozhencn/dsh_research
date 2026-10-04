# 验证范围、复现及结果

环境与SHA见[baseline](baseline.md)。所有命令在固定checkout执行；新增示例从报告validation脚本进入真实runtime。没有提供模型凭据，没有真实业务文件／工具副作用验证。JSONL测试采用仓库测试自己的临时数据和mock；POSIX lease用本机native flock。

## 结果与计数口径

原研究 V01—V07 去重后：**22 个仓库测试文件＋1 个自定义测试文件，1,001 个用例通过，1 个条件跳过。** 本次 V08 另运行 7 个不重复的仓库测试文件，201 个用例通过、0 失败或跳过；V10 再运行 6 个不重复仓库文件，302 passed、0 failed/skipped；累计为 **35 个仓库文件＋1 个自定义文件，1,504 passed、1 conditional skipped**。不是全仓测试，也不是代码覆盖率。

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
