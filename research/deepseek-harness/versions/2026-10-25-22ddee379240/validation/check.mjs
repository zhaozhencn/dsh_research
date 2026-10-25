import { createRequire } from 'node:module'
import { readFile, writeFile, unlink } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
const here = dirname(fileURLToPath(import.meta.url))
const report = resolve(here, '..')
const repo = resolve(process.argv[3] ?? '.sources/deepseek-harness-2026-10-25')
const mode = process.argv[2]
const req = createRequire(resolve(repo, 'package.json'))
const ts = req('typescript')
const sha = '22ddee3792402c3e70ec5f86a63c3e3e895a2f60'
if (spawnSync('git', ['rev-parse', 'HEAD'], { cwd: repo, encoding: 'utf8' }).stdout.trim() !== sha) throw new Error('Wrong checkout SHA')
const raw = ts.readConfigFile(resolve(repo, 'tsconfig.base.json'), ts.sys.readFile).config
let result
let cmd
const config = resolve(repo, `.research-${mode}-${process.pid}.${mode === 'typecheck' ? 'json' : 'config.ts'}`)
try {
  if (mode === 'build') {
    for (const name of ['sum-tool', 'route-policy']) {
      const source = resolve(report, 'examples', name, 'index.ts')
      const compiled = ts.transpileModule(await readFile(source, 'utf8'), { compilerOptions: { target: ts.ScriptTarget.ES2024, module: ts.ModuleKind.ESNext } })
      await writeFile(resolve(report, 'examples', name, 'lib/index.js'), compiled.outputText)
    }
    result = { status: 0, stdout: 'Compiled two ESM plugins; bare peer imports retained.\n', stderr: '' }
    cmd = ['typescript.transpileModule', 'sum-tool/index.ts', 'route-policy/index.ts']
  } else if (mode === 'typecheck') {
    const paths = Object.fromEntries(Object.entries(raw.compilerOptions.paths).map(([key, values]) => [key, values.map(p => resolve(repo, p.startsWith('./vendor/') ? p.replace('/src', '/lib/types') : p))]))
    await writeFile(config, JSON.stringify({ compilerOptions: { ...raw.compilerOptions, paths, composite: false, incremental: false, declaration: false, declarationMap: false, noEmit: true, rewriteRelativeImportExtensions: false }, files: [resolve(report, 'examples/sum-tool/index.ts'), resolve(report, 'examples/route-policy/index.ts'), resolve(here, 'mock-runtime.ts')] }))
    cmd = ['corepack', 'pnpm', 'exec', 'tsc', '-p', config]
    result = spawnSync(cmd[0], cmd.slice(1), { cwd: repo, encoding: 'utf8', maxBuffer: 20e6 })
  } else if (mode === 'test') {
    const aliases = Object.entries(raw.compilerOptions.paths).filter(([k]) => !k.includes('*')).sort(([a], [b]) => b.length - a.length).map(([find, paths]) => ({ find, replacement: resolve(repo, paths[0]) }))
    await writeFile(config, `import { defineConfig } from 'vitest/config'\nimport { standardDecoratorPlugin, vitestExecArgv } from './vitest.shared.ts'\nexport default defineConfig({ plugins:[standardDecoratorPlugin()],resolve:{alias:${JSON.stringify(aliases)}},test:{include:[${JSON.stringify(resolve(here, 'extensions.spec.ts'))}],pool:'forks',execArgv:vitestExecArgv,maxWorkers:1,testTimeout:10000}})\n`)
    cmd = ['corepack', 'pnpm', 'exec', 'vitest', 'run', '--config', config, '--reporter=default', '--reporter=json', `--outputFile.json=${resolve(here, 'extensions-results.json')}`]
    result = spawnSync(cmd[0], cmd.slice(1), { cwd: repo, encoding: 'utf8', maxBuffer: 20e6 })
  } else throw new Error('Use typecheck, build, or test')
  const log = `SHA: ${sha}\nCWD: ${repo}\nCOMMAND: ${JSON.stringify(cmd)}\n${result.stdout ?? ''}${result.stderr ?? ''}\nEXIT: ${result.status}\n`
  await writeFile(resolve(here, `logs/${mode}.log`), log)
  process.stdout.write(log)
  const ledger = resolve(here, 'runs.json')
  const records = await readFile(ledger, 'utf8').then(JSON.parse).catch(() => [])
  records.push({ id: `${mode}-${records.filter(r => r.id.startsWith(mode+'-')).length+1}`, sha, cwd: repo, command: cmd, scope: '两个参考扩展；固定源码 runtime＋受控模型；编译插件产物', purposes: mode === 'test' ? ['normal-loop', 'abnormal-or-cancel', 'extension-runtime', 'cleanup'] : ['extension-type'], inputs: '本目录及 examples 源码', expected: 'exit 0', actual: `exit ${result.status}; see log`, exit_code: result.status, outcome: result.status === 0 ? 'passed' : 'failed', log_path: `validation/logs/${mode}.log`, limitations: ['源码 alias 集成，未验证发布包安装、UI和真实模型'] })
  // Keep each attempt so later fixes never overwrite failure logs.
  const current = records.at(-1)
  const attemptLog = `validation/logs/${current.id}.log`
  await writeFile(resolve(report, attemptLog), log)
  current.log_path = attemptLog
  await writeFile(ledger, JSON.stringify(records, null, 2)+'\n')
  process.exitCode = result.status ?? 1
} finally { await unlink(config).catch(() => {}) }
