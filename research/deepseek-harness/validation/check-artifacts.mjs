import { readdir, readFile, writeFile, stat } from 'node:fs/promises'
import { resolve, dirname, relative } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { createRequire } from 'node:module'
import { execFileSync } from 'node:child_process'
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'..')
const repo=resolve(process.argv[2]??resolve(here,'../../../.sources/deepseek-harness'))
const req=createRequire(resolve(repo,'package.json'))
const { JSDOM }=req('jsdom')
const dom=new JSDOM('<!doctype html><html><body></body></html>')
globalThis.window=dom.window;globalThis.document=dom.window.document
const {default:mermaid}=await import(pathToFileURL(req.resolve('mermaid')).href)
mermaid.initialize({startOnLoad:false,securityLevel:'strict'})
const sha='5badb15009ae1756c3afe0ae0cef1faafc290ccc'
const failures=[],diagrams=[],mdFiles=[]
async function walk(dir) {for(const d of await readdir(dir,{withFileTypes:true})){const path=resolve(dir,d.name);if(d.isDirectory()) await walk(path);else if(d.name.endsWith('.md'))mdFiles.push(path)}}
await walk(root)
let links=0,sourceLinks=0
for(const path of mdFiles) {
 const content=await readFile(path,'utf8')
 if(/\{\{E\d+\}\}/.test(content))failures.push(`unexpanded evidence: ${relative(root,path)}`)
 for(const m of content.matchAll(/\[[^\]\n]+\]\(([^)\s]+)\)/g)) {
  const href=m[1];links++
  if(href.startsWith('https://github.com/deepseek-ai/deepseek-harness/blob/')) {
   sourceLinks++;const parts=/\/blob\/([^/]+)\/(.*?)(?:#L(\d+)(?:-L(\d+))?)?$/.exec(href)
   if(!parts||parts[1]!==sha){failures.push(`source SHA mismatch: ${href}`);continue}
   try{const source=await readFile(resolve(repo,parts[2]),'utf8');const n=source.split('\n').length;if(parts[3]&&!(+parts[3]>0&&+(parts[4]??parts[3])<=n))failures.push(`source range: ${href}`)}catch{failures.push(`missing source: ${href}`)}
  }else if(!/^(https?:|mailto:|#)/.test(href)){
   const destination=resolve(dirname(path),decodeURIComponent(href.split('#')[0]))
   if(destination===resolve(here,'artifact-check.json')) continue // Produced by this checker after all validations.
   try{await stat(destination)}catch{failures.push(`missing local link: ${relative(root,path)} -> ${href}`)}
  }
 }
 let index=0
 for(const m of content.matchAll(/```mermaid\s*\n([\s\S]*?)```/g)){
  index++;try{await mermaid.parse(m[1]);diagrams.push({file:relative(root,path),index,ok:true})}catch(error){failures.push(`Mermaid: ${relative(root,path)} #${index}: ${error.message}`);diagrams.push({file:relative(root,path),index,ok:false})}
 }
}
const evidence=JSON.parse(await readFile(resolve(root,'appendices/evidence.json'),'utf8'))
for(const [id,e] of Object.entries(evidence)){
 try{const text=await readFile(resolve(repo,e.path),'utf8');if(!(e.start>0&&e.end>=e.start&&e.end<=text.split('\n').length))failures.push(`bad anchor ${id}`)}catch{failures.push(`missing evidence ${id}`)}
}
const inventory=JSON.parse(await readFile(resolve(root,'appendices/workspace-inventory.json'),'utf8'))
const coverage=JSON.parse(await readFile(resolve(root,'appendices/coverage.json'),'utf8'))
const pnpm=JSON.parse(await readFile(resolve(root,'appendices/pnpm-workspaces.json'),'utf8'))
const members=new Set(inventory.map(x=>x.path));if(members.size!==341||coverage.length!==members.size||pnpm.length!==members.size+1)failures.push('workspace counts mismatch')
for(const name of ['sum-tool','route-policy']){
 const code=await readFile(resolve(root,'examples',name,'lib/index.mjs'),'utf8')
 if(code.includes('.sources/deepseek-harness'))failures.push(`bundled source copy in ${name}`)
 const pkg=JSON.parse(await readFile(resolve(root,'examples',name,'package.json'),'utf8'))
 try{await stat(resolve(root,'examples',name,pkg.main))}catch{failures.push(`missing package main ${name}`)}
}
const current=execFileSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8'}).trim()
const trackedStatus=execFileSync('git',['status','--short'],{cwd:repo,encoding:'utf8'}).trim()
if(current!==sha)failures.push('checkout SHA changed')
if(trackedStatus)failures.push(`checkout dirty: ${trackedStatus}`)
const result={sha,markdown_files:mdFiles.length,checked_links:links,checked_source_links:sourceLinks,evidence_anchors:Object.keys(evidence).length,workspace_members:members.size,pnpm_projects:pnpm.length,mermaid_version:'11.16.0',diagrams,source_checkout_clean:trackedStatus==='',checks:'local targets / source SHA and ranges / source anchors / diagram parser / workspace counts / compiled peer imports / checkout status',note:'Mermaid parse only; no visual rendering or browser E2E. GitHub links validated against fixed checkout, not individually fetched online.',failures,ok:failures.length===0}
await writeFile(resolve(here,'artifact-check.json'),JSON.stringify(result,null,2)+'\n')
console.log(JSON.stringify(result,null,2));process.exitCode=result.ok?0:1
