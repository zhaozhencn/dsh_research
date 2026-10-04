import { createRequire } from 'node:module'
import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
const here=dirname(fileURLToPath(import.meta.url))
const repo=resolve(process.argv[2] ?? resolve(here,'../../../.sources/deepseek-harness'))
const ts=createRequire(resolve(repo,'package.json'))('typescript')
for(const name of ['sum-tool','route-policy']) {
 const pkg=resolve(here,'../examples',name)
 const file=resolve(pkg,'index.ts')
 const result=ts.transpileModule(await readFile(file,'utf8'),{fileName:file,reportDiagnostics:true,compilerOptions:{target:ts.ScriptTarget.ES2024,module:ts.ModuleKind.ESNext,verbatimModuleSyntax:true}})
 const errors=(result.diagnostics??[]).filter(d=>d.category===ts.DiagnosticCategory.Error)
 if(errors.length) throw new Error(ts.formatDiagnosticsWithColorAndContext(errors,{getCanonicalFileName:f=>f,getCurrentDirectory:()=>repo,getNewLine:()=> '\n'}))
 await mkdir(resolve(pkg,'lib'),{recursive:true})
 await writeFile(resolve(pkg,'lib/index.mjs'),result.outputText)
 console.log(`built ${name}/lib/index.mjs; bare package imports preserved (TypeScript ${ts.version})`)
}
