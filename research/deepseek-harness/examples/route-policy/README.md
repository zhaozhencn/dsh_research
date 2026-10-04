# 示例二：agent/request 路由插件

适用固定SHA见[总说明](../README.md)。[index.ts](index.ts)包含Config Schema、非空验证、inject和完整waterfall callback；[package.json](package.json)固定Cordis／Agent／Schemastery peer；[lib/index.mjs](lib/index.mjs)已构建并用于运行测试。

`await next()`取得默认或后继配置，spread保留其他字段，替换provider/model；await前后检查取消。该seam不能改写messages；路由选择会由Loop写入request/header。真实类型和时机：[agent/request](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/agent/src/runtime-types.ts#L321-L337)。

依赖Cordis4.0.5-alpha.1、dsh-agent0.2.1-alpha.1、Schemastery3.18.5-alpha.1，TS6.0.3、Node24运行。目录同第一个示例；独立patch使用research-route-policy包名，model/provider必须换成实际已注册路由，随仓patch的mock只用于解释离线验证配置。

本次验证：原路由base→挂插件后policy，adapter请求与Session header一致；unload后已有Session保持最后logged header，而新Agent回到base。另一个测试在create.setup中agentCtx.plugin挂载policy，只有对应Agent被影响。流式partial输出后cancel，visible prefix写入assistant/message，Turn以aborted结算，driver归idle。

没有定时器、连接或外部副作用；ctx.on自动effect清理，不维护第二套route状态。清理handle.dispose／root Fiber；若业务要求现有Session改回base，应明确挂后继policy，而不能把卸载误当状态回滚。完整安装／编译／测试命令见[总说明](../README.md)，运行证据见[测试日志](../../validation/examples-tests.log)。
