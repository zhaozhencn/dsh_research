# 示例一：research_sum 工具

适用固定SHA见[总说明](../README.md)。[index.ts](index.ts)是完整代码，[package.json](package.json)固定peer版本，[lib/index.mjs](lib/index.mjs)是已构建并运行测试的ESM。

工具参数a、b是required number；execute返回有限number；output.schema验证canonical value，output.render转换为模型可读文本。纯运算明确声明isConcurrencySafe并检查exec.signal。注册已由tools.register归属Fiber effect，不重复包ctx.effect，也没有业务磁盘副作用。契约：[defineTool](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/packages/core/tools/src/schema.ts#L554-L632)。

目录：index.ts、package.json、README.md、cordis.patch.yml、lib/index.mjs。安装／类型／构建／离线运行命令完整列于[总说明](../README.md)；单独接入时只安装本包并使用本目录patch。源码依赖Cordis4.0.5-alpha.1和dsh-tools0.2.1-alpha.1，验证编译器TS6.0.3。

本次真实结果：挂载后adapter第一步请求research_sum(2,3)，第二步收到tool result“5”；Session两次step/start和completed turn/end。malformed a='bad'产生INVALID_ARGS结果，body没有给出正常sum。卸载plugin之后tools.get('research_sum')为空。未挂插件时不会发布该工具schema；缺少工具的调用交给runtime unknown-tool分支。

清理通过owned handles.dispose和ctx.fiber.dispose；本工具没有额外网络／文件资源。最终5个扩展场景中2个核心工具用例＋相关卸载断言通过；见[测试](../../validation/examples.spec.ts)。生产profile安装／激活配置仅准备，未运行真实provider。
