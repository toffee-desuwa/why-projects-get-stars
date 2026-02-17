# Case Study 02 — Docs-first repo (README is intentionally thin)

Repo: shadcn-ui/ui  
Mode: README-first (v0.2)

## What happened
The README is extremely short and mostly points to external docs:
- It has a clear positioning sentence
- It includes a docs link
- It does NOT include install/usage/quickstart steps in the README itself

## Why this matters
In v0.2, our evaluator is intentionally README-first:
- We treat the README "first screen" as the main decision surface for starring.
- If a repo is docs-first (README thin, docs heavy), the v0.2 score will trend lower.

This is not a bug. It's a scope definition.

## Next
Roadmap: add an optional mode to follow 1-step links (docs/getting-started) and score the combined text.
