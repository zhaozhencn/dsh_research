import { writeFile, unlink } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
const here = dirname(fileURLToPath(import.meta.url))
const repo = resolve(process.argv[2] ?? resolve(here, '../../../.sources/deepseek-harness'))
const cfg = resolve(repo, `.research-vitest-${process.pid}.config.ts`)
const source = `import { defineConfig } from 'vitest/config';
import ts from 'typescript';
import { resolve } from 'node:path';
const config=ts.readConfigFile('./tsconfig.base.json',ts.sys.readFile).config;
const aliases=Object.entries(config.compilerOptions.paths).filter(([k])=>!k.includes('*')).sort(([a],[b])=>b.length-a.length).map(([find,paths])=>({find,replacement:resolve(paths[0])}));
import { standardDecoratorPlugin, vitestExecArgv } from './vitest.shared.ts';
export default defineConfig({ plugins: [standardDecoratorPlugin()], resolve: {alias: aliases},
test: { include: [${JSON.stringify(resolve(here,'examples.spec.ts'))}], pool: 'forks', execArgv: vitestExecArgv, maxWorkers: 1, testTimeout: 10000 }});`
try {
  await writeFile(cfg, source)
  const r = spawnSync('corepack', ['pnpm','exec','vitest','run','--config',cfg], {cwd: repo, stdio: 'inherit'})
  process.exitCode = r.status ?? 1
} finally { await unlink(cfg).catch(() => {}) }
