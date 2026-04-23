---
name: project-tracking-updater
description: "Update roadmap, changelog, and architecture tracking documents after QA PASS for each completed phase, preserving traceable project progress."
---

# Project Tracking Updater

Use this skill after a QA PASS to keep project tracking current.

## Trigger

Only run when QA gate report has explicit PASS.

## Required Inputs

- phase identifier
- QA PASS report path
- phase summary and changed files
- architecture-impact note (yes/no)

## Update Targets

- `docs/development-roadmap.md`
- `docs/project-changelog.md`
- `docs/system-architecture.md` (only if structural impact)
- `CLAUDE.md` change history (only for harness changes)

## Update Rules

1. Do not update anything before QA PASS.
2. Record facts only from evidence artifacts.
3. Keep entries concise and diff-friendly.
4. Keep roadmap status and changelog entries consistent.

## Minimum Roadmap Entry Fields

- phase
- status
- progress percent
- blockers (if any)
- next dependency

## Minimum Changelog Entry Fields

- date
- phase
- key changes
- fixes
- risk/security notes

## Output

Return:

- list of updated files
- concise summary of what changed
- unresolved questions
