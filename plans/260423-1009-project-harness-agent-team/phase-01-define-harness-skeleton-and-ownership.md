---
title: "Phase 01 define harness skeleton and ownership"
description: "Plan the harness file layout, role boundaries, and file ownership model."
status: pending
priority: P1
effort: 2h
branch: main
tags: [phase-01, harness, ownership]
created: 2026-04-23
---

# Context Links

- `/Users/february10/Documents/interviewCopilot/interview-copilot-brief6.md`
- `/Users/february10/Documents/interviewCopilot/plans/260423-1735-hybrid-interview-copilot-implementation/plan.md`

# Overview

- Priority: P1
- Status: pending
- Outcome: define minimal harness files before any implementation team starts

# Key Insights

- Repo has no `README.md`, no project `CLAUDE.md`, no `.claude/agents`, no `.claude/skills`, no `docs/`
- Need bootstrap that is simple, explicit, and safe for a small repo
- YAGNI: create only role files needed for this team, not a generic framework

# Requirements

## Functional
- Define exact files to create under `.claude/agents/`
- Define exact files to create under `.claude/skills/`
- Define project `CLAUDE.md` content goals
- Define role ownership and handoff rules

## Non-functional
- No overlapping ownership
- Easy to audit by reading file names only
- New contributors can follow without session history

# Architecture

## Team pattern
- Lead/controller owns orchestration only
- Frontend agent owns UI/app routes/components only
- Backend agent owns API/contracts/services only
- Researcher agent is read-only support when blocked
- QA gate agent owns validation reports and release/pass decision
- Project-tracker agent owns docs updates after each passed phase

## Exact files to create

### `/Users/february10/Documents/interviewCopilot/.claude/agents/`
- `frontend-implementer.md`
- `backend-api-implementer.md`
- `blocker-researcher.md`
- `qa-gate-verifier.md`
- `project-tracker.md`
- `team-orchestrator.md`

### `/Users/february10/Documents/interviewCopilot/.claude/skills/`
- `phase-gate-playbook/SKILL.md`
- `project-tracking-updater/SKILL.md`
- `blocker-triage-research/SKILL.md`
- `handoff-package-checklist/SKILL.md`

### `/Users/february10/Documents/interviewCopilot/CLAUDE.md`
- repo harness purpose
- role map
- execution flow
- QA gate requirement
- tracking update requirement
- change history section

# Related Code Files

## Files to modify
- None in this planning task

## Files to create later
- Files listed above
- `/Users/february10/Documents/interviewCopilot/docs/development-roadmap.md`
- `/Users/february10/Documents/interviewCopilot/docs/project-changelog.md`
- `/Users/february10/Documents/interviewCopilot/docs/system-architecture.md`
- `/Users/february10/Documents/interviewCopilot/README.md`

## Files to delete
- None

# Implementation Steps

1. Create project `CLAUDE.md` as single entrypoint for harness rules and history.
2. Add six agent definition files with explicit role scope, inputs, outputs, and ownership globs.
3. Add four narrow skills for gating, tracking, blocker research, and handoff formatting.
4. Add `docs/` tracking files after harness basics exist.
5. Keep all role prompts aligned with current hybrid implementation plan.

# Todo List

- [ ] Define exact agent filenames
- [ ] Define exact skill filenames
- [ ] Define ownership globs per role
- [ ] Define `CLAUDE.md` sections
- [ ] Define bootstrap docs list

# Success Criteria

- Every team role has one file
- Every file has one owner
- Harness entrypoint exists and points to agent/skill usage
- No file overlap between frontend and backend roles

# Risk Assessment

- High: vague role prompts cause overlapping edits -> mitigate with ownership globs + forbidden files list
- Medium: too many skills add complexity -> mitigate with 4 focused skills max
- Low: missing README causes onboarding confusion -> mitigate by creating README in first implementation phase

# Security Considerations

- Researcher role remains read-only unless explicitly reassigned
- QA agent validates no secrets added to tracked files
- `CLAUDE.md` must prohibit client-side API key handling

# Next Steps

- Phase 02 defines runtime workflow, gate logic, and handoff contracts
