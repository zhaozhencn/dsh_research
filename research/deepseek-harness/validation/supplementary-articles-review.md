# 补充专栏17—28逐篇复核

本次复核响应“仔细检查并确认文章已经生成并符合要求”，依据原[文档列表与大纲](../appendices/supplementary-article-outlines.md)和项目`source-code-article-refiner`完成标准，检查实际文件、全部正文及图示。结论：12篇正文已经生成；经过本轮修正，满足本批源码研究文章的结构、来源、调用衔接、关键数据、图文组织和工程心得要求。

这是文稿与证据复核，不把文章完成等同于企业产品验收，也不以代码段数量代替技术深度。

## 1. 检查方法与结果

|要求|本轮检查|结果|
|---|---|---|
|实际生成|逐文件读取17—28正文，核对目录入口及三份配套文档|12篇齐全，无占位稿|
|保留原结构|直接从原大纲提取八章标题，与每篇正文比较|96个主体章节一致|
|开头有整体描述|逐篇阅读业务问题、入口、主线、对象及第一张图|均有完整导入|
|连续源码解释|读取全部正文，核查caller、callee、参数来源、await、结果consumer及分支|修正后可沿交接阅读|
|核心数据|检查创建输入、Skill候选、表单revision、Remote结果、bindings、投递记录与授权等结构|声明、字段和消费关系有依据|
|源码真实|对每段摘录执行固定Git对象或本仓库示例原文/hash比较|当前151段；原148段均保留|
|优势、代价与心得|逐篇核对正文工程取舍和收尾，判断是否能对应具体实现|均回到本篇机制与实践|
|专业术语|检查正文与SVG；Agent、Turn、Step等保留英文|通过|
|至少3—4张图|检查PNG/SVG配对、解码、尺寸、caption和所在章节，并查看48张图联系表|每篇4张，共48组|
|保护原文|比较原00—16篇及资产的156项hash；比较本轮修改前的新文章标题与代码块集合|原156项不变；新文章八章及原代码保留|
|实测不混淆|核对测试命令、退出码、日志、mock及未验证范围|本轮不重复宣称历史行为测试|

机器检查与逐篇语义阅读分别记录。检查器已改为根据各篇图文计划核对图片位置，不再要求所有文章都把图片固定放在相同四章；章标题还直接与原大纲比较，避免只拿正文生成的清单自证结构正确。

## 2. 逐篇确认

|篇次|已核对的关键链路与数据|结论|
|---|---|---|
|[17](../articles/17-agent-creation-composition.md)|Registry→factory→prepare/setup→持久追加→publish；完整创建输入、preset generation与退出handle|符合；补齐输入后半段，收紧政策版本保存建议|
|[18](../articles/18-skill-instruction-loading.md)|provider.list→分层候选→snapshot→tool-skill目录→Registry.get/provider.get；AGENTS.md独立路径|符合；Scope图移到选择章节，区分两级get|
|[19](../articles/19-settings-config-writeback.md)|describe→来源投影→write→Editor锁内检查→compose/write/reconcile；revision、secret、volatile|符合；说明补偿本身也可能失败|
|[20](../articles/20-plugin-package-management.md)|install control、包管理进程、selection、解析表、HMR与remove；各阶段ChangeResult|符合；图中不再暗示安装直接调用inspect|
|[21](../articles/21-fullstack-plugin-development.md)|manifest→boot graph→Client；save→form.mutate→Remote→Gateway→Host write→view/store/Slot|符合；新增两个真实caller摘录，补齐读写支线过渡|
|[22](../articles/22-sdk-acp-web-integration.md)|lazy runtime→initialize→Session/prompt→receipt→idle/result→close；ACP/Web契约差异|符合；改正stdio SDK的HTTP超时措辞|
|[23](../articles/23-mcp-connection-lifecycle.md)|generation、tools/list、候选构建与swap、执行闭包、resources/instructions、重连与dispose|符合；工具调用图移到实际调用章节|
|[24](../articles/24-ptc-program-execution.md)|presentation→run_code→bindings→resolve/run/execute→IPC→内部工具→finish/drain|符合；补上run到私有execute的真实参数交接|
|[25](../articles/25-workflow-schedule-hooks.md)|Workflow子任务、Schedule持久投递、Hook协议/bridge；三种终态与owner|符合；三种机制回到各自章节，组合边界独立展开|
|[26](../articles/26-enterprise-data-remote-execution.md)|业务工具/grant/connector→受限查询；SSH helper、execution world、prepare/start；幂等receipt|符合；按大纲分开业务与远端主线，补知识检索的新增契约|
|[27](../articles/27-identity-credentials-tenancy.md)|请求信任、per-operation凭据、Subject/TaskSpec、live Agent binding、资源复核与预算|符合；凭据图和装配图回到各自位置，补resume/delegation授权前提|
|[28](../articles/28-build-package-distribution.md)|Host/Typert/Client构建顺序、exports/files、build record/digest、局部tarball消费与升级验证|符合；载体图移到应用产物章节|

## 3. 本次实质修正

17篇的Session metadata建议原先过宽。上游SessionHeader有固定字段，不能直接添加任意policyRevision；现在明确由企业TaskSpec保存并通过SessionId关联。新增创建输入声明，区分创建期signal与运行取消、可信setup约定与隔离保证。

21篇原先从describe读取跳到Host write，过渡不足。现在追入`SettingsFormModel.save()`和`ConfigForm.mutate()`，展示ops、baseline revision、排队及Remote调用；新增两段固定提交原文。表单的SettingsFormScope也与Agent Scope区分。

25、26、27篇存在正文与章节主题错位，本轮重排原摘录并补真实转场：Workflow清理归入子任务章节，Schedule投递归入Schedule章节，Hook执行归入Hooks章节；26篇按业务connector、SSH执行、业务效果、恢复分开；27篇先完成凭据读写，再进入身份授权。全部八章标题和原源码块保留。

19篇补偿错误、22篇SDK transport措辞和24篇run/execute衔接已收紧。26篇的知识检索接口明确标为企业新增设计，当前工单实现没有向量库或完整RAG pipeline。27篇说明恢复与child需要显式重新授权，不能由Context继承推导业务权限。

配图已按实际消费者重新安排，相关图定义、篇章计划、来源顺序与当前hash同步。原48组图仍保留；27篇两张图的内容与caption重新匹配。未新增不属于源码事实的调用箭头。

## 4. 本轮验证与限制

本轮实际执行源码/大纲/图片检查、全研究链接和Mermaid检查、原专栏与第00篇检查、修改前后代码与标题保护比较，以及`git diff --check`。命令、退出码与结果见[复核记录](supplementary-articles-review.json)；源码与图片详情见[当前检查结果](supplementary-articles-check.json)。

本轮仅修改文稿、图定义及文稿检查器，没有改动上游runtime或企业示例代码。因此，没有重跑上一批848项通过、1项平台跳过的行为测试；该结果仍作为[既有运行记录](supplementary-articles-validation.md)保留。

21篇采用上游已有完整设置插件，26、27篇采用本仓库企业参考实现，28篇的实际pack验收仅导入`./ledger`。真实模型、MCP/SSH/SSO、浏览器E2E、完整发行安装与生产部署仍未验证。文章中的教学方案不升级为这些外部系统的完成保证，公众号编辑器也未实际预览或发布。
