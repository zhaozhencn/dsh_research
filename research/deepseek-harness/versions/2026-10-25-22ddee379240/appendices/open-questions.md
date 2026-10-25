# 待验证项与适用限制

本轮交付插件开发相关当前报告和两个参考插件，保证级别 limited。以下未被本批测试证明：

|问题|当前证据|下一步可执行验收|
|---|---|---|
|发布包是否能在干净 home 真正装载|编译 ESM + source aliases|完整目标构建，pack/install consumer，profile dump + activation|
|真实模型的 schema、取消、错误和价格语义|受控 adapter 的真实 Loop|已授权测试账号下 provider smoke；记录网络错误与取消|
|UI/Client 模块、重连和卡片回放|manifest 消费源码和官方规则|构建 ./client，浏览器挂载/卸载、重连、持久结果展示|
|企业 Remote 端到端资源授权|RemoteAccess host 单测|真实 Peer/Gateway、聚合过滤、事件推送、撤权/过期链|
|企业工单助手能否迁到 rc.3|旧示例停在 alpha.1|迁移创建/选模/投影/executor，重跑业务幂等和撤权 suite|
|共享 Session 目录升级与普通 fork|源码 V4 和官方迁移说明|副本目录中测试 reader/writer、resume、fork、备份恢复|
|SSH/PTC/MCP/Teams 全链|本批只沿工具准入与接口读影响|逐 provider 复核其实现/配置/清理并运行实际用例|
|跨平台、原生 sandbox 和生产容量|macOS arm64 host addon 与单测|目标 OS 的执行/拒绝、清理和发布产物检查；负载另测|

源码还显示 architecture 对 Persistence `export` 的表述与抽象接口不一致，本报告按真实接口集成。未发现足以从本批测试推导吞吐上限、SLA、多租户隔离或任意插件热替换无损保证的数据。
