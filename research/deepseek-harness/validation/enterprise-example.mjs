import { createRequire } from 'node:module'
import { readFile, writeFile, mkdir, unlink, readdir } from 'node:fs/promises'
import { spawnSync, execFileSync } from 'node:child_process'
import { resolve, dirname, basename } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const mode = process.argv[2]
const repo = resolve(process.argv[3] ?? resolve(here, '../../../.sources/deepseek-harness'))
const pkg = resolve(here, '../examples/enterprise-harness')
const req = createRequire(resolve(repo, 'package.json'))
const ts = req('typescript')
const sha = '5badb15009ae1756c3afe0ae0cef1faafc290ccc'
if (execFileSync('git', ['rev-parse', 'HEAD'], { cwd: repo, encoding: 'utf8' }).trim() !== sha) {
  throw new Error('Unexpected source baseline')
}
const files = (await readdir(pkg)).filter(name => name.endsWith('.ts')).map(name => resolve(pkg, name))
const raw = ts.readConfigFile(resolve(repo, 'tsconfig.base.json'), ts.sys.readFile).config

if (mode === 'build') {
  await mkdir(resolve(pkg, 'lib'), { recursive: true })
  for (const file of files) {
    const built = ts.transpileModule(await readFile(file, 'utf8'), {
      fileName: file, reportDiagnostics: true,
      compilerOptions: { target: ts.ScriptTarget.ES2024, module: ts.ModuleKind.ESNext, verbatimModuleSyntax: true },
    })
    if (built.diagnostics?.some(d => d.category === ts.DiagnosticCategory.Error)) throw new Error(`Build: ${file}`)
    await writeFile(resolve(pkg, 'lib', basename(file).replace(/\.ts$/, '.js')), built.outputText)
  }
  console.log(`Built ${files.length} ESM modules; peer imports preserved; TypeScript ${ts.version}`)
} else if (mode === 'typecheck') {
  const paths = Object.fromEntries(Object.entries(raw.compilerOptions.paths).map(([key, values]) => [key,
    values.map(path => resolve(repo, /^(\.\/)?vendor\//.test(path) ? path.replace('/src', '/lib/types') : path)),
  ]))
  const config = resolve(repo, `.enterprise-tsconfig-${process.pid}.json`)
  try {
    await writeFile(config, JSON.stringify({ compilerOptions: {
      ...raw.compilerOptions, paths, composite: false, incremental: false, declaration: false,
      declarationMap: false, noEmit: true, rewriteRelativeImportExtensions: false,
    }, files: [...files, resolve(here, 'mock-runtime.ts')] }))
    const result = spawnSync('corepack', ['pnpm', 'exec', 'tsc', '-p', config], { cwd: repo, stdio: 'inherit' })
    process.exitCode = result.status ?? 1
  } finally { await unlink(config).catch(() => {}) }
} else if (mode === 'test') {
  const config = resolve(repo, `.enterprise-vitest-${process.pid}.config.ts`)
  const source = `import { defineConfig } from 'vitest/config';
import ts from 'typescript'; import { resolve } from 'node:path';
import { standardDecoratorPlugin, vitestExecArgv } from './vitest.shared.ts';
const raw=ts.readConfigFile('./tsconfig.base.json',ts.sys.readFile).config;
const alias=Object.entries(raw.compilerOptions.paths).filter(([k])=>!k.includes('*'))
  .sort(([a],[b])=>b.length-a.length).map(([find,paths])=>({find,replacement:resolve(paths[0])}));
export default defineConfig({plugins:[standardDecoratorPlugin()],resolve:{alias},test:{
  include:[${JSON.stringify(resolve(here, 'enterprise-example.spec.ts'))}],pool:'forks',
  execArgv:vitestExecArgv,maxWorkers:1,testTimeout:10000,reporters:['default','json'],
  outputFile:{json:${JSON.stringify(resolve(here, 'enterprise-tests.json'))}}}});`
  try {
    await writeFile(config, source)
    const result = spawnSync('corepack', ['pnpm', 'exec', 'vitest', 'run', '--config', config], { cwd: repo, stdio: 'inherit' })
    process.exitCode = result.status ?? 1
  } finally { await unlink(config).catch(() => {}) }
} else { throw new Error('Usage: node enterprise-example.mjs typecheck|build|test [checkout]') }
