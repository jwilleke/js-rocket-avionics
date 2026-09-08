---
title: CLAUDE.md
description: Guidance for Claude Code and other AI agents in this repo.
---

# CLAUDE.md

Guidance for Claude Code (and other AI agents) in this repo.

Read `AGENTS.md` and `private/project_log.md` before starting any work.
Session continuity lives in the `▶ Resume here` block at the top of `TODO.md`.
Priorities are GitHub issue labels; `TODO.md` is their generated mirror.

## What this is

<!-- One or two sentences: what the repo does and its primary purpose. -->
<!-- Example: "A self-hosted ESPHome firmware project for car positioning and garage door -->
<!-- control, integrated with Home Assistant via ESPHome's native API." -->

## Build / run

<!-- The exact commands an agent needs to compile, test, and run this project. -->
<!-- Example: -->
<!-- ```bash -->
<!-- npm run dev       # start dev server -->
<!-- npm test          # run test suite -->
<!-- npm run build     # production build -->
<!-- ``` -->

## Architecture

<!-- Key files, directories, and data-flow summary. -->
<!-- What to read first when diving into the code. -->
<!-- Any generated files that must not be hand-edited. -->

## Conventions

### One source of truth per fact, and link to it

__Operator, 2026-09-08.__ Every statement has an owner. Write it once, in the page that owns it, and __link__ from everywhere else. Restating a fact in a second place is not helpful redundancy — it is a copy that goes stale silently, and this repo has already shipped several: `module-pinouts.md` still called a measured part unmeasured, `BOM.md` still called it the last blocker, and `design.md` still named a reed switch three weeks after it was superseded. Each was true when written.

__A sentence you cannot keep current is worse than a link.__ If a statement will move — a measurement, a part choice, a status, a date, an open question — do not copy it. Name the owner and point at it.

| Owner | Owns |
|---|---|
| [`docs/BOM.md`](docs/BOM.md) | part numbers, vendors, masses |
| [`docs/module-pinouts.md`](docs/module-pinouts.md) | dimensions, pin orders, footprint inputs, what has actually been measured |
| [`hardware/*.md`](hardware/README.md) | what each part is, its interfaces, the traps that are properties of the object — and the vocabulary used for it |
| [`docs/design.md`](docs/design.md) | why the architecture is what it is |
| GitHub issues | what is open, what is decided, and when |
| `private/project_log.md` | what happened in a session |

__Applies to prose as much as to tables__, and to a summary just as much as to a number: a paragraph restating another page's reasoning is a fork of that reasoning.

## Security / secrets

<!-- Anything that must never be committed. -->
<!-- Real data, credentials, keys, PHI, etc. -->
<!-- Only fill this in if there are non-obvious pitfalls. -->
