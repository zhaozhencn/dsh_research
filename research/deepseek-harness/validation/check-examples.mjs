import { createRequire } from 'node:module'
import { writeFile, unlink } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
const here=dirname(fileURLToPath(import.meta.url))
const repo=resolve(process.argv[2] ?? resolve(here,'../../../.sources/deepseek-harness'))
const req=createRequire(resolve(repo,'package.json'))
const ts=req('typescript')
const raw=ts.readConfigFile(resolve(repo,'tsconfig.base.json'),ts.sys.readFile).config
const paths=Object.fromEntries(Object.entries(raw.compilerOptions.paths).map(([k,v])=>[k,v.map(p=>resolve(repo,p.startsWith('./vendor/') || p.startsWith('vendor/') ? p.replace('/src','/lib/types') : p))]))
const config=resolve(repo,`.research-tsconfig-${process.pid}.json`)
try {
 await writeFile(config,JSON.stringify({compilerOptions:{...raw.compilerOptions,paths,composite:false,incremental:false,declaration:false,declarationMap:false,noEmit:true,rewriteRelativeImportExtensions:false},files:[resolve(here,'../examples/sum-tool/index.ts'),resolve(here,'../examples/route-policy/index.ts'),resolve(here,'mock-runtime.ts')]}))
 const r=spawnSync('corepack',['pnpm','exec','tsc','-p',config],{cwd:repo,stdio:'inherit'})
 process.exitCode=r.status??1
} finally {await unlink(config).catch(()=>{})}
