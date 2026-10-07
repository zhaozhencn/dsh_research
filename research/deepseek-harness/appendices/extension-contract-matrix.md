# DSH 二次开发扩展契约矩阵

基线为 `0.2.1-alpha.1` / `5badb15009ae1756c3afe0ae0cef1faafc290ccc`。这份矩阵把17—28篇的接口、挂载位置、关键数据与退出责任放到同一视图；具体字段、代码行号和 caller/callee 关系沿文章继续阅读。它是固定版本的研究结论，不是跨版本稳定 API 承诺。

## 1. 扩展入口与生命周期

|扩展面|生产者与消费入口|挂载/数据契约|失败与退出责任|解读|
|---|---|---|---|---|
|Agent composition|Registry → factory → setupAndPublish|sessionId、Session、setup、AgentHandle|setup/通知失败清理；holder await dispose|[17](../articles/17-agent-creation-composition.md)|
|preset|register/activate → mount/composeFrom|standing Scope、generation、users、retired|旧 revision 最后使用者退出才释放|[17](../articles/17-agent-creation-composition.md)|
|Skill|provider.list/get → Registry → tool-skill|candidate/summary/definition；cwd/Scope/revision|不完整观察不缓存；取消/撤销；last-good catalog|[18](../articles/18-skill-instruction-loading.md)|
|Settings|describe/write → ConfigEditor.edit|Entry id、revision、volatile、value/base/user|锁内检查；写盘后 reconcile；失败尝试恢复|[19](../articles/19-settings-config-writeback.md)|
|Plugin Manager|管理 RPC/CLI → change → pnpm/apply|profile files、requestId、stage/application|退出进程树后恢复；已加载包可需 restart|[20](../articles/20-plugin-package-management.md)|
|Client/UI|Loader → graph → Client apply/Slots|dsh.client、exports、SlotMap、snapshot/face|Context effects 撤销；迟到结果检查代际|[21](../articles/21-fullstack-plugin-development.md)|
|Remote|Client carrier → Gateway → Service view|generated descriptor、args、invocation、result|定义撤销后禁止 strict→SRC 降级；stream 需退出|[21](../articles/21-fullstack-plugin-development.md)|
|SDK/ACP/Web|各入口 → Agent factory/Session|入口各自创建、接纳、事件、取消契约|连接/订阅/Session/进程分层关闭|[22](../articles/22-sdk-acp-web-integration.md)|
|MCP|supervisor → syncTools → ToolRuntime|server/raw/public name、generation、schema|fetch 失败留旧代；swap 失败归零；dispose 等收敛|[23](../articles/23-mcp-connection-lifecycle.md)|
|PTC|presentation → run_code → runtime|program、bindings、spec、control channel|程序停止后 bridge 结算在途 tools；runtime 等进程退出|[24](../articles/24-ptc-program-execution.md)|
|Workflow|start → guest/host → SubagentRun|meta/script/args、parent、callId、run.result|返回前 parse 可 throw；返回后 stopReason；等待 children|[25](../articles/25-workflow-schedule-hooks.md)|
|Schedule|stored tasks → timer → Session inbox|record、sessionId、receipt/history|flush 与 task commit 分别确认；停止 timer 再关 domain|[25](../articles/25-workflow-schedule-hooks.md)|
|Hooks|dialect bridge → runHook → merge|payload、matcher、signal、decision/context|合并能力和 bridge 映射分别核对；post hook 不撤回效果|[25](../articles/25-workflow-schedule-hooks.md)|
|SSH/providers|consumer → fs/subprocess/sandbox → ssh|private targets、execution world、helper digest/lease|不自动重连重放；断线效果未知；清理等待|[26](../articles/26-enterprise-data-remote-execution.md)|
|Credentials|consumer operation → provider.resolve|Ref 与 Key 两个空间；来源与 writability|每次操作重读；锁内写；撤销旧 snapshot|[27](../articles/27-identity-credentials-tenancy.md)|
|企业授权（新增）|trusted provisioning → Agent binding → ledger|Subject、TaskSpec、object identity、tenant/resource|await 后重查；撤权拒绝旧 grant；DB 事务确认 receipt|[27](../articles/27-identity-credentials-tenancy.md)|
|发行|Host/Typert → Client → pack consumer|exports/files、public env、artifact digest|构建失败不留旧 record；安装/升级需独立验收|[28](../articles/28-build-package-distribution.md)|

## 2. 应明确区分的完成事实

`appReady` 表示 Host 激活条件已满足；`AgentHandle` 创建返回表示实例已发布；SDK 的 `messageId` 表示输入接纳；Schedule receipt 表示 durable inbox delivery；Workflow result 表示脚本和子任务结算；业务 receipt 才表示指定外部效果取得确认。

这些事实之间不能只靠名称推断。企业任务状态表应保留它们的关联身份，例如 taskId、sessionId、messageId、callId、operationId 与政策版本；每种身份由相应生产者产生，不由模型随意决定。

## 3. 使用矩阵选择实现层

先确定扩展改变哪一类事实：新增能力挂到 scoped registration；更换执行环境实现 provider seam；对外接入修改具体入口；资源隔离在企业控制面和资源服务实现；界面展示消费 Remote/snapshot；最终产品交付检查真实产物。

再确定 disposer 归属、await 后的有效性检查和提交点。比如远端请求在授权后开始，不意味着响应可以不经再次核验进入 Session；停止程序不意味着已提交数据库写入被撤销。把这些责任写进接口，后续版本变化才容易沿调用链做回归。

## 4. 证据范围

[本批验证](../validation/supplementary-articles-validation.md)包含源码摘录、图片和链接检查、选定上游测试、编译企业示例、tarball ledger smoke。完整浏览器、生产 SSO/vault、真实模型/企业后端、多节点调度和跨平台发行没有由这些结果证明。
