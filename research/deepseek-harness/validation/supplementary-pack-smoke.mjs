/** Offline consumer smoke for the existing enterprise example's packed ledger. */
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs'
import { dirname, resolve, join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import assert from 'node:assert/strict'
const here = dirname(fileURLToPath(import.meta.url))
const root = resolve(here, '../../..')
const example = resolve(here, '../examples/enterprise-harness')
const parent = resolve(root, '.sources/supplementary-pack-work')
mkdirSync(parent, { recursive: true })
const dir = mkdtempSync(join(parent, 'consumer-'))
const packed = JSON.parse(execFileSync('npm', ['pack', '--ignore-scripts', '--json', '--pack-destination', dir], { cwd: example, encoding: 'utf8' }))[0]
const tarball = join(dir, packed.filename)
execFileSync('tar', ['-xzf', tarball, '-C', dir])
const manifest = JSON.parse(readFileSync(join(dir, 'package/package.json'), 'utf8'))
for (const entry of Object.values(manifest.exports)) assert.ok(existsSync(join(dir, 'package', entry)), entry)
const { EnterpriseLedger } = await import(pathToFileURL(join(dir, 'package/lib/ledger.js')).href)
const subject = { tenantId: 'pack-tenant', actorId: 'pack-actor' }
const spec = { ...subject, taskId: 'pack-task', sessionId: 'pack-session', policyRevision: 1,
  provider: 'fixture', model: 'fixture', maxAttempts: 2, maxTokens: 128,
  expiresAt: Date.now() + 60_000, ticketId: 'T-PACK', expectedVersion: 1, canClose: true }
const db = join(dir, 'consumer.sqlite')
let ledger = new EnterpriseLedger(db)
try {
  ledger.createTask(spec)
  ledger.putTicket(subject.tenantId, { ticketId: spec.ticketId, title: 'Packed consumer', status: 'open', version: 1 })
  const grant = ledger.authorize(subject, spec.taskId, spec.sessionId)
  const first = ledger.closeTicket(grant)
  assert.deepEqual(ledger.closeTicket(grant), first)
  assert.deepEqual(ledger.auditPhases(spec.taskId), ['business-committed'])
  ledger.close()
  ledger = new EnterpriseLedger(db)
  assert.deepEqual(ledger.closeTicket(grant), first)
  const record = { passed: true, node: process.version, package: manifest.name, version: manifest.version,
    tarballSha256: createHash('sha256').update(readFileSync(tarball)).digest('hex'),
    files: packed.files.map(row => row.path), exportsExist: Object.keys(manifest.exports),
    observations: ['unpacked ledger imports without monorepo aliases', 'business receipt stable on retry', 'receipt survives database reopen', 'one business audit record'],
    limitations: ['Only ./ledger is imported: other plugin exports require their declared exact peer dependencies', 'No clean full DSH install, real model, browser, Desktop, native platform matrix or publication was performed'] }
  writeFileSync(join(here, 'supplementary-pack-check.json'), JSON.stringify(record, null, 2) + '\n')
  console.log(JSON.stringify(record, null, 2))
} finally { ledger.close() }
