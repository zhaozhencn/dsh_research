# Repository Guidelines

## Project Structure & Module Organization

This repository contains Chinese, source-backed DeepSeek Harness research and runnable reference extensions.

- `prompt.md`: research requirements.
- `research/deepseek-harness/`: numbered reports and navigation.
- `articles/` and `articles/assets/` within that directory: 16 technical articles, PNG/SVG diagrams, and diagram data.
- `examples/`: TypeScript plugins, package manifests, configuration patches, and compiled `lib/` artifacts.
- `validation/` and `appendices/`: tests, verification scripts, logs, source evidence, and baseline metadata.
- `skills/harness-research-sync/`: reusable research workflow and Python tooling.
- `skills/source-code-article-refiner/`: maintained article-refinement skill; `.agents/skills/source-code-article-refiner` links here for repository-scoped discovery. Edit the maintained directory to update the skill.
- `.sources/`: ignored upstream checkouts and local environments; never commit this directory.

## Build, Test, and Development Commands

Run from the repository root. Runtime checks require the pinned checkout at `.sources/deepseek-harness`, installed dependencies, and prepared vendor declarations. Follow the example README for setup; there is no root application build command.

```sh
# Strict types, ESM compilation, and enterprise integration tests
node research/deepseek-harness/validation/enterprise-example.mjs typecheck
node research/deepseek-harness/validation/enterprise-example.mjs build
node research/deepseek-harness/validation/enterprise-example.mjs test
# Report links, source ranges, and Mermaid syntax
node research/deepseek-harness/validation/check-artifacts.mjs
# Research tooling tests using isolated Git fixtures
python3 -m unittest discover -s skills/harness-research-sync/scripts -p 'test_*.py' -v
```

The enterprise example was verified with Node 24.19.0. Check its manifest and baseline before changing versions.

## Coding Style & Naming Conventions

Use two-space TypeScript indentation, single quotes, semicolon-free ESM, and explicit type imports. Use four-space Python indentation. Follow adjacent code; this repository has no root formatter or lint configuration. Prefer kebab-case filenames, numbered report names, `camelCase` functions, and `PascalCase` types. Keep research prose professional and in Chinese.

## Testing & Research Evidence

Use Vitest `*.spec.ts` tests for runtime contracts and Python `test_*.py` files for tooling. No repository-wide coverage threshold is configured. Test changed behavior, including relevant failure, cancellation, authorization, and cleanup paths. Rebuild changed plugins before testing compiled artifacts.

Pin source citations to the recorded full SHA. Distinguish source facts, official documentation, runtime verification, inference, and proposals. Preserve failed runs and record commands, exit codes, scope, and limitations; mock tests do not establish production readiness. Follow `skills/harness-research-sync/SKILL.md` for research and version synchronization.

## Commit & Pull Request Guidelines

History includes `Initial commit` and `docs: add ...`. Use concise imperative subjects; use `docs:` for research changes. PRs should describe the outcome, affected reports/examples, source baseline, executed checks, and remaining limitations. Link relevant issues and include diagram previews when visuals change. Preserve unrelated work and exclude credentials, temporary databases, and local environments.
