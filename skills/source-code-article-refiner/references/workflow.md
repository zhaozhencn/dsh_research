# 结构化计划与连续源码写作

## 先建立可填写的工作计划

复制 `../assets/article-plan.json` 到任务工作目录，填入真实信息；空数组表示尚未完成，不能被当作已复核。一个计划对应一篇文章。系列另列目标篇目及保护范围，先从认可的样篇提取标准，逐篇填写自己的机制，不复用样篇函数名。

|字段|填写要求|
|---|---|
|`scope`|目标路径、读者、中心问题、保留规则、受保护路径、单篇／系列／版本模式|
|`source_baseline`|仓库路径、完整SHA、可选官方URL，以及历史运行证据所属SHA|
|`mechanism_map`|真实入口、职责、关系边和独立支线；边标记call、emit、subscribe、read、return等|
|`article_plan`|开篇整体描述、原有主体章节、每节解决的问题与前后衔接对象|
|`steps`|按下述分析单元记录caller、callee、输入输出、consumer、条件与摘录|
|`data_contracts`|关键声明、字段、生产消费、状态、提交与释放；不适用项写明原因|
|`figure_plan`|图型、所在步骤、表达关系、节点来源、术语、输出与实际查看状态|
|`lessons`|实现事实、解决问题、可迁移做法、适用条件及关联步骤|
|`review`|检查命令、退出码、语义复核结论、限制与历史证据；默认状态为pending|

数组内的记录采用以下字段约定。只填写已核实的内容；`null`表示待调查，不代表机制不存在。源码引用含`sha`、`path`、`start`、`end`、`raw_sha256`和可选`url`，可直接使用辅助脚本输出。

```json
{
  "edge": {"from": null, "to": null, "kind": null, "evidence": []},
  "section": {"original_heading": null, "current_heading": null, "question": null, "handoff": null},
  "step": {
    "id": null, "caller": null, "callee": null,
    "previous_output": null, "input": null, "core_decision": null,
    "output": null, "consumer": null, "await_boundary": null,
    "commit_point": null, "branches": [], "excerpts": []
  },
  "data_contract": {
    "symbol": null, "declaration": null, "fields": [],
    "producer": null, "consumers": [], "state_transitions": [],
    "commit_point": null, "release_owner": null
  },
  "figure": {
    "type": null, "after_step": null, "purpose": null,
    "nodes": [], "edges": [], "evidence": [],
    "outputs": [], "visually_reviewed": false
  },
  "lesson": {"fact": null, "problem": null, "practice": null, "conditions": null, "step_ids": []}
}
```

以上是记录形状，将相应对象放入计划的各数组；不要把未填写的示例作为正式交付。`fields`逐项包含名称、作用、生产和消费；图的`edges`同样标明call、return、read、emit等性质。记录中确实不适用的等待或释放字段，填入说明而非虚构机制。

## 每个步骤的分析单元

1. 前一步产出了什么数据、资格或状态？当前函数为什么在此调用？
2. 给出caller内的调用现场。进入callee前，解释参数从哪里来，哪些已经准备、哪些仍待判断。
3. 展示最小但足够的原文范围，解释条件、状态变化、await与副作用。摘录保留真实函数、字段和分支，不拼接几段代码冒充一个原函数。
4. 展示关键声明或字段表，区分身份、配置、状态、结果和资源。解释生产者与consumer，而非逐字翻译类型。
5. 指出返回值、闭包、事件或持久记录交给谁。返回原caller时说明结果怎样改变原来的控制流。
6. 在正文中连接异常、取消、卸载或恢复支线；声明这条边属于直接调用、事件派发还是状态读取。

这些问题是研究检查项，不是要求每步生成相同六个小标题。写成自然段落，以“对象为何出现、如何变化、由谁继续处理”为骨架。

### 衔接示例

不充分：“然后分析 `step()` 的内部实现。”

更有效：“`preStep()`已返回本次执行的准入结果和上下文。`turn()`先处理拒绝分支，只有允许执行时才把这份`PreparedStep`交给`step()`。因此进入后者前，要先看这份数据包含哪些内容，以及它是否已经代表执行成功。”

此示例来自DeepSeek Harness既有研究，仅说明写法。迁移到其他项目或版本时重新核对关系和类型，不把示例作为源码证据。

## 开篇、正文和结尾的责任

开篇回答关注点、整体职责、入口和主线，避免百科定义后直接进入局部函数。主体保留原有关注领域；按真实机制安排顺序，必要时在节首说明装配与执行的切换。

正文同时解释实现过程、关键数据、收益与适用限制。企业方案标明“扩展建议”，指出现有接入点和新契约。使用Agent、Turn、Step、attempt、Inbox、Fiber、surface及源码符号；中文解释用于降低理解成本，不用“代理／回合”替换既定Agent／Turn。不要全局替换网络proxy等含义不同的词。

结尾从正文提炼工程做法。例如由并行生产与有序提交推导“分别观察执行完成、历史提交和资源释放”，并交代适用条件；不要仅说“提升并发与可靠性”。收益与不足在相关步骤分析，结尾以具体收获回应中心问题。

## 三种模式

- **单篇深化：** 先保存原状，再填计划、改文稿、改配图、复核。邻近文章默认保持原状。
- **系列同步：** 样篇转为共同检查标准；逐篇研究独有的caller、数据与生命周期。全部目标完成后更新导航和当前统计，不覆盖样篇和历史记录。
- **版本同步：** 先调查新旧完整SHA、改变的契约和证据。保留旧验证，新正文按新SHA重摘源码；删除或改写旧代码须有版本原因。不能仅更换链接SHA和行号就宣布完成同步。
