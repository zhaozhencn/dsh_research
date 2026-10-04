# Harness 契约复核地图

下面是本次 DeepSeek Harness 研究提炼的查找方向，不是新版本的能力承诺。参考旧基线 `5badb15009ae1756c3afe0ae0cef1faafc290ccc`；目录、名称或实现改变时按新 tree 与符号追踪，不能硬套旧路径。

优先 `rg --files` 和 `rg -n` 搜索真实定义、导出、实现、注册、调用与测试。动态链路需要结合配置和依赖实现。读取截断时按范围补读，不能将搜索摘要当实现阅读。

| 议题／搜索线索 | 核验问题 | 典型误判 |
|---|---|---|
| Cordis、Context、Service、inject | 作用域、提供与消费、激活、dispose；第三方框架与产品责任 | 一切皆插件⇒所有东西可任意替换 |
| emit、parallel、serial、waterfall、intercept | 同步／异步、等待顺序、返回值、异常传播、撤销 | 把所有事件当同一种广播 |
| Session、Turn、Step、Agent | 类型、运行对象、事件边界、开始／提交／结束、无 Step 路径 | 凭名称发明实体嵌套 |
| input、queue、wake、loop | 入队与接纳、追加输入、继续条件、锁和并发 | 输入到达即进入本轮 prompt |
| history、prompt、context、schema | 请求组装顺序、不可变边界、工具选择、重试是否重组 | 注册工具一定向每个模型暴露 |
| provider、adapter、route、request | 调度与具体模型适配、流、重试、工具回写、取消 | 调度与 provider 视为单层 |
| tool、approval、pool、shell、fs | 选择／执行、并发、前后拦截、缺失结果、底层取消与副作用 | 拒绝／取消保证回滚外部行为 |
| session、event、store、flush、format、migration | append时点、flush、持久／内存／投影、读写迁移、分支 | 展示历史等于重放工具、写入即落盘 |
| profile、bundle、patch、loader、reload | 入口差异、叠加顺序、schema、默认值、重新挂载与代码更新 | 配置reload等于任意代码热替换 |
| native、binding、sandbox、flock、pty | 声明／实际平台、编译与加载、文件／进程强制层 | 配置 scope 等于安全隔离 |
| stream、rpc、subscribe、projection | producer、传输、客户端状态、重连与补偿 | 进程内事件直接跨进程广播 |
| auth、credential、tenant、permission | 检查层、凭据生命周期、进程与租户边界、真实入口差异 | Agent作用域等于多租户保障 |

每条强结论使用定义、实现、消费者与验证交叉核验：

- **完整替换**：公开契约、入口、隐含调用与状态／事件兼容均需说明。只有配置覆盖不能证明完全替换。
- **热替换**：分别说明注册撤销、配置重挂载、模块缓存更新、前端重建和进程重启；验证在途任务和释放责任。
- **恢复／回放／分支**：历史展示、投影重建、请求重建和工具重新执行分别解释。外部模型与工具副作用不默认可复现。
- **重试／超时／熔断**：指出负责层、触发条件、范围、次数、输入是否重组与实际取消；没有机制就说明未发现的搜索与追踪范围。
- **缺陷／性能／泄漏**：给触发与证明。潜在风险注明前提；没有测量不写性能排名，没有复现不写发生频率。

如旧结论基于 Cordis、Schema 或模型 SDK，读取目标锁文件及对应依赖源码／官方版本资料。manifest range 与实际解析版本分别记录，不能把第三方行为归为 Harness 自身实现。
