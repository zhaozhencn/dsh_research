# 创建时的持久模型策略

适用固定 SHA `22ddee3792402c3e70ec5f86a63c3e3e895a2f60`，DSH 0.2.1-rc.3、Cordis 4.0.5、Schemastery 3.18.5。独立 ESM 插件，入口 `lib/index.js`。

Config 必填 provider/model；插件在 `agent/created` 调 `agent.model.select()`。放进 Agent setup 只影响这个 Agent；部署级挂载影响可见的新建/恢复 Agent。给已经创建的 Agent 后挂载不会补发 created。该策略不强制每次请求重选，用户后续显式切换仍有效，也不做模型发现、健康熔断或价格决策。

它替换历史 agent/request 路由改写；当前版本旧写法会在调用 adapter 前失败。卸载只移除 created listener，Session 内的 model/selection 不删除。若要更换已有会话，校验目标路线后显式 select；从下一个尚未准备的 Step 生效。

自定义 setup 如需切换提示可另装一次 `installModelSelection(agentCtx)`；有该配置的宿主不重复装。插件本身不安装提示，避免和宿主叠加。

按[环境准备](../README.md)从研究根目录执行 typecheck/build/test。预期目标 Agent 与普通 Agent 分别 policy/base，卸载后目标 Agent 保留 policy；pre-step 内新选择只影响后续 Step。取消链由同批测试覆盖。配置中的 mock 仅供可控 adapter 测试，生产替换为真实已注册/已验证的 provider/model。本批无真实模型和发布安装验证；结束进程后按上级说明清理自建临时 home。
