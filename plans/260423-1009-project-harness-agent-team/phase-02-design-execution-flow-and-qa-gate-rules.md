---
title: "Phase 02 design execution flow and QA gate rules"
description: "Plan orchestration sequence, blocker handling, and incremental QA gates."
status: pending
priority: P1
effort: 3h
branch: main
tags: [phase-02, orchestration, qa]
created: 2026-04-23
---

# Context Links

- `/Users/february10/Documents/interviewCopilot/plans/260423-1009-project-harness-agent-team/phase-01-define-harness-skeleton-and-ownership.md`
- `/Users/february10/Documents/interviewCopilot/plans/260423-1735-hybrid-interview-copilot-implementation/plan.md`

# Overview

- Priority: P1
- Status: pending
- Outcome: define exact execution mode and pass/fail logic per phase

# Key Insights

- Final-only QA is too late; each phase needs a stop/go decision
- Frontend and backend can run in parallel only after shared contract approval
- Researcher must be on-demand support, not a permanent extra hop

# Requirements

## Functional
- Define default execution chain
- Define blocker escalation path
- Define QA gate inputs, outputs, and failure handling
- Define what project-tracker updates after gate pass

## Non-functional
- Minimize idle time
- Keep gate evidence objective
- Ensure rollback path for each phase

# Architecture

## Execution mode
- Default: sequential phases
- Inside a phase: parallel frontend/backend only if contract file ownership is already locked
- Researcher: spawned only on blocker, ambiguity, external dependency, or failed experiment
- QA gate: mandatory before phase completion
- Tracker update: mandatory after QA pass, before next phase opens

## Phase gate logic
1. Lead declares scope, dependencies, owned files, success criteria.
2. Frontend/backend deliver implementation plus self-check evidence.
3. If blocked, researcher produces decision memo with options, risks, recommendation.
4. QA gate agent validates unit/integration/manual criteria for that phase.
5. If QA fails, phase returns to owners; next phase stays blocked.
6. If QA passes, project-tracker updates docs and marks phase complete.
7. Lead opens next phase.

## Incremental QA matrix
- Phase bootstrap/architecture: file existence, prompt consistency, ownership conflicts, docs links
- Shared contracts/protocols: schema validation, example payload parity, backwards-compatible defaults
- Backend phases: route tests, auth/error handling, migration safety, API contract tests
- Frontend phases: component states, loading/error UX, API integration stubs, browser sanity
- Integration phases: end-to-end journey, latency budget, rollback drill, no-secret verification

## Gate artifact format
- `plans/reports/qa-gate-{date}-{phase}.md`
- Fields: scope, evidence, failed checks, risk rating, pass/fail, rollback note, unblock recommendation

# Related Code Files

## Files to modify
- None in this planning task

## Files to create later
- `/Users/february10/Documents/interviewCopilot/.claude/agents/qa-gate-verifier.md`
- `/Users/february10/Documents/interviewCopilot/.claude/skills/phase-gate-playbook/SKILL.md`
- `/Users/february10/Documents/interviewCopilot/plans/reports/qa-gate-*.md`

## Files to delete
- None

# Implementation Steps

1. Encode execution order in `CLAUDE.md`.
2. Put ownership + acceptance criteria template into orchestrator agent file.
3. Put QA checklist templates into `phase-gate-playbook` skill.
4. Require rollback note in every phase completion report.
5. Block next-phase task creation until QA pass report exists.

# Todo List

- [ ] Define phase lifecycle
- [ ] Define blocker escalation flow
- [ ] Define QA artifact schema
- [ ] Define pass/fail criteria examples
- [ ] Define rollback expectations

# Success Criteria

- Every phase has measurable pass criteria
- Failed QA clearly blocks next phase
- Researcher involvement has explicit triggers
- Rollback instructions exist for each phase

# Risk Assessment

- High: parallel work on shared contracts causes churn -> mitigate with contract-first gate before split work
- Medium: QA becomes subjective -> mitigate with checklist + evidence links + explicit pass/fail line
- Medium: blocker research slows work -> mitigate with timeboxed researcher memo and recommendation format

# Security Considerations

- QA gate checks secrets, auth boundaries, logging hygiene
- Researcher cannot introduce unverified code paths
- Rollback must avoid partial migrations or orphaned config

# Next Steps

- Phase 03 defines tracking docs and mandatory update workflow
