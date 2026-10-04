#!/usr/bin/env node
// Parse report diagrams with dependencies from an explicit local project.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

function argumentsOf(argv) {
  const result = {};
  for (let i = 0; i < argv.length; i += 2) {
    if (!['--report', '--dependencies', '--min-diagrams'].includes(argv[i]) || !argv[i + 1])
      throw new Error('Usage: --report <directory> --dependencies <project> [--min-diagrams <number>]');
    result[argv[i]] = argv[i + 1];
  }
  if (!result['--report'] || !result['--dependencies']) throw new Error('Missing report or dependency project');
  return result;
}
function markdownFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const filename = path.join(dir, entry.name);
    return entry.isDirectory() ? markdownFiles(filename) : entry.isFile() && entry.name.endsWith('.md') ? [filename] : [];
  }).sort();
}
function packageVersion(entry, name) {
  let dir = path.dirname(entry);
  while (true) {
    const manifest = path.join(dir, 'package.json');
    if (fs.existsSync(manifest)) {
      const pkg = JSON.parse(fs.readFileSync(manifest, 'utf8'));
      if (pkg.name === name) return pkg.version;
    }
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}
try {
  const args = argumentsOf(process.argv.slice(2));
  const root = path.resolve(args['--report']);
  const minimum = Number(args['--min-diagrams'] ?? 1);
  if (!Number.isInteger(minimum) || minimum < 0) throw new Error('Invalid --min-diagrams');
  const localRequire = createRequire(path.join(path.resolve(args['--dependencies']), 'package.json'));
  const { JSDOM } = localRequire('jsdom');
  const dom = new JSDOM('<!doctype html><html><body></body></html>');
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
  globalThis.DOMParser = dom.window.DOMParser;
  const entry = localRequire.resolve('mermaid');
  const mermaid = (await import(pathToFileURL(entry).href)).default;
  mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });
  const records = [];
  for (const filename of markdownFiles(root)) {
    const content = fs.readFileSync(filename, 'utf8');
    const pattern = /^\s*```mermaid[^\n]*\r?\n([\s\S]*?)^\s*```\s*$/gm;
    for (const match of content.matchAll(pattern)) {
      const row = { file: path.relative(root, filename), line: content.slice(0, match.index).split('\n').length };
      try {
        const result = await mermaid.parse(match[1]);
        if (!result) throw new Error('Parser did not accept diagram');
        records.push({ ...row, outcome: 'passed' });
      } catch (error) {
        records.push({ ...row, outcome: 'failed', error: String(error.message ?? error) });
      }
    }
  }
  const ok = records.length >= minimum && records.every(r => r.outcome === 'passed');
  console.log(JSON.stringify({ ok, mermaid_version: packageVersion(entry, 'mermaid'), parsed: records.length,
    minimum, records, limits: ['Syntax parsing only; diagram rendering and source semantics require separate review.'] }, null, 2));
  dom.window.close();
  process.exitCode = ok ? 0 : 1;
} catch (error) {
  console.error(JSON.stringify({ ok: false, error: String(error.message ?? error), outcome: 'blocked-or-invalid' }));
  process.exitCode = 2;
}
