# 固定版本扩展示例

适用SHA `5badb15009ae1756c3afe0ae0cef1faafc290ccc`；Harness API包0.2.1-alpha.1，Cordis4.0.5-alpha.1、Schemastery3.18.5-alpha.1；Node24.19.0、pnpm11.7.0、TypeScript6.0.3验证。每例都有独立package.json和ESM源码／编译文件。

- [sum-tool](sum-tool/README.md)：canonical number输出、typed args、取消、并发标记与卸载。
- [route-policy](route-policy/README.md)：agent/request路由配置、scope、持久header与取消。
- [enterprise-harness](enterprise-harness/README.md)：企业任务授权、独立 policy／工具插件、持久预算、截止取消与本地业务幂等；另有 16 个已通过的真实 Loop／SQLite 用例，不计入下文原有五用例。

## 离线复现：从当前工作区执行

```sh
cd /Users/zz/prj/dsh_research/.sources/deepseek-harness
corepack pnpm install --frozen-lockfile --ignore-scripts
corepack pnpm exec tsc -b vendor/cordis vendor/schemastery
cd /Users/zz/prj/dsh_research
node research/deepseek-harness/validation/check-examples.mjs
node research/deepseek-harness/validation/build-examples.mjs
node research/deepseek-harness/validation/run-examples.mjs
```

脚本均可接受checkout绝对路径作为第一个参数。默认路径按报告位置推导。`check-examples`严格检查两插件和mock；vendor引用其独立配置生成的声明，不把它们源码强行并入严格program。`build-examples`用TypeScript transpileModule输出JS，保留bare package imports，类型正确性由前一个独立检查证明。测试加载**编译后的lib/index.mjs**并跑真实Loop，以源码aliases将runtime包统一指向本次checkout。

预期：typecheck退出0；build生成每包`lib/index.mjs`；Vitest **5 passed**。包括工具正常两Step、invalid args、route前后变化与卸载、新Agent不再受路由listener影响、取消，以及setup挂载只作用于本Agent。无需模型凭据；mock只提供流，实际接纳、事件提交、工具与清理由真实runtime完成。测试结束清理所有AgentHandle与root Fiber，临时配置自动删除。

最初用tsdown源码paths构建会引入依赖源码副本，破坏单例边界；最终改为独立转译保留package import。不要复制一套Cordis／Scope／LLM进自定义插件，生产应用与插件应共享同一peer runtime。

## 官方profile接入配置（准备完成，完整profile启动未在本研究运行）

前提：同版本已构建／已安装的`dsh`可用；将当前报告绝对路径换成实际所在路径。该步骤用新的临时Harness home避免碰真实配置。下面安装是已准备的接入命令，本次只执行了上面的离线测试，不声称真实SDK进程接入通过。

```sh
export DSH_HOME="$(mktemp -d -t harness-research)"
dsh plugin --profile sdk add /Users/zz/prj/dsh_research/research/deepseek-harness/examples/sum-tool /Users/zz/prj/dsh_research/research/deepseek-harness/examples/route-policy
dsh --profile sdk --patch /Users/zz/prj/dsh_research/research/deepseek-harness/examples/profile.patch.yml --dump-config
dsh --profile sdk --patch /Users/zz/prj/dsh_research/research/deepseek-harness/examples/profile.patch.yml
```

`dsh plugin --profile <name> <pnpm args>`是真实CLI形式；插件安装与entry activation是两步，patch通过insert挂载包。route-policy示例配置为provider=`mock`／model=`policy`，**生产profile若无mock adapter，不应直接发送请求**；先将其改为该profile已注册且经过验证的provider/model。SDK需上层client发送JSON-RPC；不是交互终端对话程序。

清理：终止该SDK进程，unset DSH_HOME，删除自己创建的临时home；编译文件只在示例lib目录，重建可覆盖，删除示例lib即可移除输出。不要对现有正式home执行清理命令。

类型、构建和运行日志分别见[types](../validation/examples-typecheck.log)、[build](../validation/examples-build.log)、[tests](../validation/examples-tests.log)。
