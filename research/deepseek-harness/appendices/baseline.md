# 固定研究基线

|字段|记录|
|---|---|
|研究开始|2026-10-04 07:17:19，Asia/Shanghai|
|官方仓库|https://github.com/deepseek-ai/deepseek-harness|
|选择|开始时官方默认分支master的可获取HEAD，随后detach固定|
|完整SHA|`5badb15009ae1756c3afe0ae0cef1faafc290ccc`|
|commit时间／标题|2026-10-03 11:48:13 +08:00；Merge release相关PR；精确git记录可本地show复核|
|版本|根及Harness产品包0.2.1-alpha.1；不是stable发布|
|checkout|`/Users/zz/prj/dsh_research/.sources/deepseek-harness`|
|历史深度|clone depth100；相关diff限定可获取提交|
|文件／workspace|14,208 tracked；341成员；含根工具项目pnpm list共342|
|平台|macOS27.0 arm64；非Linux／Windows验证|
|Node/npm/Corepack|实际v24.19.0／11.17.0／0.35.0|
|pnpm|根packageManager声明11.7.0；实际corepack pnpm11.7.0|
|Python/Git|实际3.9.6／2.54.0 Apple Git157；未执行Python SDK|
|依赖安装|frozen lockfile、ignore-scripts；随后独立build:native-system补原生flock|
|源代码修改|研究未修改仓库tracked文件；本地构建输出为ignored；git status --short最终为空|

本机Python3.9.6仅执行清单／文稿生成脚本，不据此声称Python SDK支持该版本。SDK版本要求请见基线内pyproject；未运行其安装／测试。

## 声明、锁定与实际运行分开

|依赖／能力|声明／包版本|锁文件或实际结果|依据与限制|
|---|---|---|---|
|Node|`^22.19.0 || >=24.0.0`|实际24.19.0|根package.json；未跑其他Node lane|
|TypeScript|`^6.0.3`|锁6.0.3，类型检查及转译使用6.0.3|根pnpm-lock.yaml importer|
|Vitest|`^4.1.8`|锁4.1.8，测试日志4.1.8|原tests＋自定义tests|
|根Vite|8.0.16|锁8.0.16|根测试工具；不是Web构建版本|
|Web / Desktop Vite|`^6.0.0`|锁6.4.3|应用importer；未执行Web构建／浏览器|
|React / ReactDOM|`^18.2.0`|锁18.3.1|Web importer；未实测React UI|
|Electron|`^44.0.0`|锁44.0.0|应用manifest；未运行Desktop|
|tsdown / tsx|`^0.22.2`／`^4.22.4`|锁0.22.2／4.22.4|本地工具；最终扩展用TS转译避免source path依赖副本|
|Mermaid|11.16.0|锁11.16.0，交付语法检查使用同版|只做parse，不做截图渲染|
|Cordis|vendored package4.0.5-alpha.1|运行使用本SHA源码；types使用其单独tsconfig声明|与upstream pin版本不同|
|Schemastery|vendored package3.18.5-alpha.1|运行使用本SHA源码|第三方行为依据vendored实现|
|native/system|workspace及平台包0.1.2|本机native build成功、lease测试通过|BSD-3-Clause、Node-API支持；未测试其他平台|

关键依赖JSON由[基线收集脚本](../validation/collect-inventory.py)及锁文件读取生成：[dependency-versions.json](dependency-versions.json)。完整清单见[workspace-inventory.json](workspace-inventory.json)、[pnpm-workspaces.json](pnpm-workspaces.json)、[baseline.json](baseline.json)。

## 资料与版本一致性

正文主要使用此checkout的docs、README、类型、实现、配置与测试，以及同一git历史的实际diff；每条源链接都固定SHA。官方GitHub页面只用来确认仓库与默认分支，访问日期2026-10-04，不把未来master内容混入固定结论。源码出处与符号见[evidence-index](evidence-index.md)。

vendor/README给出upstream pin及本地修改：Cordis上游pin为4.0.0-rc.7、SHA56b3d4f725681cf4556c1a8695a709cc3b6eed74，Harness vendored release为4.0.5-alpha.1；关注Fiber teardown、Config laziness、Include patches、HMR namespace和volatile behavior时依据当前vendor实现，而非套用上游网页。[E68 · 官方说明 · `vendored upstream pins and local modifications`](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/vendor/README.md#L1-L69)

源码链接示例：[固定根manifest](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/package.json)、[固定workspace配置](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/pnpm-workspace.yaml)、[固定锁文件](https://github.com/deepseek-ai/deepseek-harness/blob/5badb15009ae1756c3afe0ae0cef1faafc290ccc/pnpm-lock.yaml)。
