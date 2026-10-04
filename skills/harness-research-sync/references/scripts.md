# 辅助脚本：机械收集与检查

脚本需 Python 3.9+、Git；主脚本仅使用标准库。不会checkout、fetch、install、执行仓库代码、自动写技术结论或修改旧报告。网络仅由 `resolve` 使用 git ls-remote；获取新对象／独立worktree及测试由执行者根据任务处理。

## resolve：调用时发现“最新”

```sh
python3 scripts/research.py resolve --remote https://github.com/deepseek-ai/deepseek-harness --out <解析结果JSON>
python3 scripts/research.py resolve --remote https://github.com/deepseek-ai/deepseek-harness --ref <branch或tag>
```

不指定ref时读remote HEAD的symref及commit；tag支持peeled commit。歧义branch/tag不自动猜。输出是当次网络发现，不是offline clone的HEAD；网络失败不能把缓存说成最新。已经给完整commit时可直接在clone中rev-parse，说明未执行最新发现。

## snapshot：从Git提交生成可复核材料

```sh
python3 scripts/research.py snapshot --repo <checkout> --target <SHA> --out <不存在的新目录> --previous <旧报告目录> --resolution <resolve输出JSON>
```

`--previous`、`--resolution`可省略；repo-url默认官方地址。输出：

- `research-state.json`：仅prepared，固定基线与模式。
- `appendices/baseline.json`：commit／环境／动态包数、旧版本。
- `tracked-files.json/.txt`、`directory-inventory.json`、`workspace-inventory.json`、`dependency-graph.json`。
- 有previous时：`changes.json`、`impact.json`、`commits.json`、`evidence-status.json`。

已有输出目录直接拒绝，不覆盖旧研究。数据来自指定commit的Git objects，因此workspace package.json没提交的编辑不会污染盘点。baseline单列工作树是否匹配目标、工作树是否dirty；运行测试前应另核验真正执行的是目标checkout。

workspace优先读提交内pnpm-workspace.yaml中的常规packages列表，支持正／负glob、`**`和简单brace alternatives；不能解析的YAML／pattern会显式失败。没有该文件时读root package.json workspaces。碰到新版复杂YAML时，执行者在干净目标checkout获取：

```sh
corepack pnpm list -r --depth -1 --json > <workspace-list.json>
python3 scripts/research.py snapshot ... --workspace-list <workspace-list.json>
```

提供的list必须恰好匹配该commit的包名、version、path；root工具项目单列，任意漏包不能靠该list自动补证。解析器支持范围之外的配置仍需完整YAML parser／pnpm核对。图中的edges只表示manifest依赖，不是static imports、DI或event关系。

## evidence-diff：旧片段的复核优先级

```sh
python3 scripts/research.py evidence-diff --repo <checkout> --previous <旧报告> --target <SHA> --out <新证据候选JSON>
```

支持旧研究的`appendices/baseline.json`和`evidence.json`。按Git rename映射查文件，并比较旧片段与新文件：identical-text、reanchored-identical-text、changed、ambiguous、missing、invalid-previous。所有review_status都保持pending；即使内容相同，也必须检查调用者和配置变化。不会覆盖evidence.json，也不会把旧运行证据变成新版本通过。

## check：结构、引用、SHA与可定位性

```sh
python3 scripts/research.py check --repo <checkout> --report <报告目录>
python3 scripts/research.py check --repo <checkout> --report <报告目录> --final
```

普通模式兼容本次legacy输出，用于锚点和文件校验。final要求新数据格式的结论／覆盖／当前SHA验证台账，检查必备文件、未完成标记、JSON对应、相对链接和当前源码链接、范围与snippet hash。仅delta.md允许明确比较旧SHA；commit链接不受当前源码SHA限制。check输出到stdout，重定向保存日志；不自动把state置complete。

它不理解结论含义，也不替代运行测试。模板式写入“reviewed”不能视为已核验。Markdown引用型链接或HTML链接若未被解析会列限制，需要执行者自行复核；不把支持的内联链接数量当全网HTTP可用性。

## Mermaid

```sh
node scripts/check-diagrams.mjs --report <报告目录> --dependencies <可解析mermaid与jsdom的Node项目目录>
```

使用目标或独立验证环境实际安装的parser；不硬编码上次11.16.0。输出parser版本、图序号和错误。缺依赖显式退出非0，不能当成零图通过；parse不等于渲染截图，也不能确认图的业务语义。依赖变化时按当前API调整后记录差异。

## 脚本自测

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

使用临时本地Git仓库，覆盖包盘点、负glob、固定对象读取、rename／旧证据迁移、缺失与歧义、拒绝覆盖和坏引用。不会联网或修改真实报告。
