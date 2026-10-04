# 验证策略

## 环境与可复现性

读取目标提交 package.json、锁文件、测试配置、scripts 和原生包安装规则，再选择 Node、包管理器和命令。不固定本次 Node/pnpm 版本、测试数或 native 包名。记录声明版本、lock解析、实际版本和平台；缺少依赖可以在独立检出安装，不修改用户开发目录。

先判断安装／构建 hooks 做什么。禁用 install scripts 后遇到原生绑定缺失时按目标包规则补构建；不能把 missing binding 当产品行为失败。另一方面，环境失败确实发生过，日志与初次失败要保留；修复后仅重跑受影响部分。

运行前确认 checkout HEAD=目标 SHA 且受测 tracked 源码未改。自编验证在报告 validation/ 或独立 harness 目录；必须改产品源码才能复现时保存 patch，注明测试基于修改版，不计纯基线通过。编译产物需来自目标源码，不混用旧版本 lib。日志脱敏但保留判断结果的必要信息。

## 分层验证

| 层级 | 可以支持的结论 | 不能替代 |
|---|---|---|
| 源码／官方测试阅读 | 实现路径、测试意图 | 本次实际运行 |
| 类型与构建 | 当前导入、签名、产物可构建 | runtime 生效、公开稳定性 |
| 目标现有测试 | 这些用例与环境下的行为 | 全仓、真实模型、其他平台 |
| 真实 runtime＋可控 mock | 完整 Loop、工具、事件、取消等受测链 | 外部 provider、真实 UI、网络、发布安装 |
| 真实服务／UI／打包安装 | 指定入口与环境实测 | 其他入口与所有平台 |

优先已有测试，新增测试针对关键不变量，不照抄实现。九类场景全部分析，但不用机械增加九套新测试。至少运行一个完整正常链和一个异常／取消链；环境不能满足时尝试离线 mock，再准确报告缺口。

重点不变量：输入接纳与提交边界、重试作用域、工具结果回写、部分成功、取消传播、持久化／投影、卸载撤销与句柄释放。同一会话并发及动态配置差异按真实实现验证，不用单元 stub 冒充全链。

## 两个独立扩展

每个示例具备独立 package.json、完整入口代码、配置、README、适用 SHA、依赖版本、安装／构建／运行命令、预期输出与清理办法。根据真实公开契约选择工具、请求拦截、provider 等两项能力。

追踪实际入口加载方式与真实导出。检查 peer 单实例要求：自定义插件不能意外打包另一份 Cordis/Context 后假装集成通过。区分 monorepo 内测试、宿主加载和 packed-install；未测试发布形态则标未测试。

分别证明扩展前后的变化、注册 scope、错误处理与 dispose 后效果撤销。类型检查退出0不代表运行通过；mock 中不应重写目标调度逻辑来“证明”同一逻辑。执行源文件还是编译产物也要写清。

## 台账与统计

每次运行保存 runs.json 条目：id、sha、cwd、command（argv数组优先）、scope、purposes、inputs、expected、actual、exit_code、outcome、log_path、限制。purposes 可用 normal-loop、abnormal-or-cancel、extension-type、extension-runtime、cleanup、repository-regression、artifact、diagram。

outcome 只有 passed/failed/blocked/skipped；passed 必须实际执行且 exit_code=0。失败和后续成功各保留一条，注明 supersedes／重跑范围。不能把零退出的空测试、仅类型检查或旧版本日志写成完整运行验证。

统计用例优先去重标识（suite/文件＋完整case名＋参数），失败重跑不能累加 passed。缺机器可去重数据时按不重叠批次报告，说明范围；不同库与自编测试分开。条件 skip 单列，不能算 passed；没有实际采集就不写固定数字。

## 报告检查

用 research.py check --final 查结构、SHA、证据锚点、覆盖、日志与链接；用 check-diagrams.mjs 解析实际所有 Mermaid 块。parser通过只证明语法，执行者仍要逐个检查节点、箭头、事件顺序、分支与正文。未安装 parser 时记录 blocked，不能说解析通过。

完整性、语义和统计由执行者自查；脚本不能确认文稿推论正确或调用链确实完整。
