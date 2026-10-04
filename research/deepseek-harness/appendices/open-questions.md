# 遗留验证与选择影响

这些是当前研究没有证明的部署／集成问题；任务要求的三篇、覆盖、证据和两个示例均已交付。无需用户参与本次完成，但上线前仍应按自己的目标环境执行下一步。

|问题|已有证据／不能证明部分|影响|最小下一步|
|---|---|---|---|
|真实DeepSeek／其他provider网络行为|mock能证Loop契约；不能证实际限流、认证、长流取消与远端token消耗|选型PoC可先用mock，上线可用性不能签字|隔离账户跑短对话、工具、流取消、429／断网smoke，保存脱敏记录|
|完整profile和打包peer单例|源码paths测试＋compiled插件已过；未执行官方发布profile或packed-install|外部插件交付仍需安装验证|同版本正式runtime、临时DSH_HOME安装两包，dump-config＋SDK initialize＋工具smoke|
|Web／Desktop真实重连|已读并跑transport／Host state tests；没有浏览器／ElectronE2E|UI展示和实际网络中断恢复不能承诺|指定Web profile／Electron构建，页面切流、断网、Host restart用官方E2E验证|
|平台shell与sandbox|源码报告full/partial，macnativeflock测试通过；未执行命令confinement|不能从mac锁测试推论Linux/Windows安全性|隔离临时文件，目标OS验证越界write／symlink／descendant退出／enforcement值|
|工具外部效果确定性|unknown outcome修复已证；无外部交易协议|不适合直接保证exactly-once付款、发信等|新增幂等connector，执行后断电／断网模拟与外部状态查询|
|企业主体与session授权|存在local auth与Host fence；未全审controller授权、多租户|直接公网共享root Host不可据此上线|定义主体资源矩阵，逐API测试cross-user读取／写入／stream／导出|
|替代Persistence provider|接口与JSONL约束已分析；未实现数据库backend|集中持久化工程量高|契约fixture覆盖write exclusivity、durable append、有效前缀、migration、resume与cancel|
|stateful provider热替换|配置／HMRtests及框架源码；没有任意资源state迁移证据|生产优先drain/restart|一个有live句柄provider，验证stop-admission→drain→remount→恢复，含activation失败|
|大型历史／并发规模|有功能tests，无benchmark或heap测量|不能宣称性能领先、容量上限或泄漏|明确目标并发／日志大小，在目标部署跑原benchmarks和资源profile|
|Python和发布资源|本机Python仅用于收集；SDKwheel、native平台包未全安装|其他语言／平台分发需独立验收|指定SDK所需Python版本和干净环境，packed runtime initialize／shutdown smoke|
|experimental Team / WebWorker|包清单与部分接口概览；没有运行team／浏览器worker|可研究，不作为已验证生产协作底座|最小roster、mailbox、task DAG、cancel与恢复fixture，再跑对应官方tests|

已确认文档差异：Persistence.export不存在而导出在独立包，fork示例seedLength与当前类型字段也有差异；建议后续修正文档，本研究没有向仓库提交issue或PR。对熔断、stable ABI、不可信插件隔离、分布式队列、租户授权均没有原生完整保证证据，新增设计与现状分开。

## 16 项架构补充后保留的边界

目标的完成／阻塞仍由调用者报告，独立验收与累计 token、费用、总时长预算没有因本次文稿补充而成为内置能力。后续若建设业务产品，应将领域验收与预算策略纳入真实任务回归。

反馈授权 Session 遥测包含历史上下文，默认脱敏 seam 原样通过；本次测试证明授权和导出契约，未验证线上采集端的保留、删除、权限或强持久审计。`present` 保存文件引用，workspace changes 的 summary/diff 依赖进程内记录和临时内容；跨重启产物验收需要单独持久保存清单、hash 与内容。本地 jobs 也不能以 Session 恢复推断为跨进程任务恢复。
