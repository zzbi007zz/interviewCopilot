---
title: "Phase 03 define tracking docs and update protocol"
description: "Plan roadmap and changelog updates that happen after each passed phase."
status: pending
priority: P2
effort: 1h
branch: main
tags: [phase-03, docs, tracking]
created: 2026-04-23
---

# Context Links

- `/Users/february10/Documents/interviewCopilot/plans/260423-1009-project-harness-agent-team/phase-02-design-execution-flow-and-qa-gate-rules.md`

# Overview

- Priority: P2
- Status: pending
- Outcome: define simple, repeatable project tracking updates after each completed phase

# Key Insights

- Repo currently has no `docs/`; tracking must be bootstrapped from zero
- Tracking must happen after QA pass, not before
- Keep docs light: roadmap + changelog first, architecture updates only when design changes

# Requirements

## Functional
- Define required docs files
- Define who updates them
- Define minimum content for each update

## Non-functional
- Fast to maintain
- Easy diff review
- Aligned with actual phase results only

# Architecture

## Tracking files to create later
- `/Users/february10/Documents/interviewCopilot/docs/development-roadmap.md`
- `/Users/february10/Documents/interviewCopilot/docs/project-changelog.md`
- `/Users/february10/Documents/interviewCopilot/docs/system-architecture.md`

## Update mechanism
- Trigger: QA gate == PASS
- Owner: `project-tracker` agent only
- Inputs: phase plan, QA report, merged implementation summary
- Outputs:
  - roadmap: phase status, percent progress, next dependencies
  - changelog: date, phase, key changes, risks/fixes
  - architecture doc: only if contracts, topology, or data flow changed

## Change history in `CLAUDE.md`
- Append dated section for harness changes only
- Include: added agents, added skills, workflow changes, gate changes

# Related Code Files

## Files to modify
- None in this planning task

## Files to create later
- tracking docs above
- `/Users/february10/Documents/interviewCopilot/.claude/agents/project-tracker.md`
- `/Users/february10/Documents/interviewCopilot/.claude/skills/project-tracking-updater/SKILL.md`

## Files to delete
- None

# Implementation Steps

1. Bootstrap roadmap with planned phases and statuses.
2. Bootstrap changelog with initial harness setup entry.
3. Add tracker prompt requiring doc update only from validated evidence.
4. Add architecture doc update rule for structural changes only.
5. Add `CLAUDE.md` change-history append rules.

# Todo List

- [ ] Define docs files
- [ ] Define update triggers
- [ ] Define update fields
- [ ] Define `CLAUDE.md` history format

# Success Criteria

- After any passed phase, docs update requires one agent action only
- Docs reflect actual QA-approved state
- No duplicate update ownership across team

# Risk Assessment

- Medium: docs drift from code -> mitigate by using QA pass report as sole source of truth
- Low: too much doc overhead -> mitigate by limiting mandatory docs to 2 core files + conditional architecture update

# Security Considerations

- Changelog must avoid secrets/internal tokens
- Architecture doc should describe boundaries, not credentials

# Next Steps

- Phase 04 closes migration, validation, and adoption plan
