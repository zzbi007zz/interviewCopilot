---
title: "Phase 04 rollout validation and migration path"
description: "Plan adoption from empty harness state to active agent-team operation with rollback."
status: pending
priority: P2
effort: 2h
branch: main
tags: [phase-04, rollout, migration]
created: 2026-04-23
---

# Context Links

- `/Users/february10/Documents/interviewCopilot/plans/260423-1009-project-harness-agent-team/plan.md`
- `/Users/february10/Documents/interviewCopilot/plans/260423-1735-hybrid-interview-copilot-implementation/plan.md`

# Overview

- Priority: P2
- Status: pending
- Outcome: define low-risk rollout order for the new harness

# Key Insights

- Current state has no harness, so migration is additive
- Backwards compatibility mainly means current planning artifacts remain valid
- Rollout should prove harness on one phase before full team adoption

# Requirements

## Functional
- Define rollout order
- Define validation steps
- Define rollback plan
- Define measurable adoption success criteria

## Non-functional
- No disruption to current implementation plan
- Easy revert by removing harness docs only

# Architecture

## Migration path
1. Add `CLAUDE.md` harness pointer and change history.
2. Add `.claude/agents/*` role files.
3. Add `.claude/skills/*` workflow skills.
4. Add `docs/` tracking files.
5. Pilot harness on next implementation phase only.
6. Review friction, then adopt for remaining phases.

## Backwards compatibility
- Existing `plans/260423-1735-hybrid-interview-copilot-implementation/*` remains source plan for product work
- New harness wraps execution only; does not replace feature plan content
- Existing contributors can still work manually if harness files are absent; controller falls back to direct planning

## Rollback plan
- If harness prompts cause confusion: disable by ignoring project `CLAUDE.md` role flow, keep product plan unchanged
- If agent prompts overlap: remove/merge offending `.claude/agents/*` file, revert to controller + one implementer + QA
- If tracking noise too high: keep roadmap only, pause changelog updates until simplified

## Validation checklist
- Dry-run one fake phase handoff without code edits
- Confirm ownership globs do not overlap
- Confirm QA gate report template blocks advancement on fail
- Confirm tracker updates only happen after pass
- Confirm blocker flow can invoke researcher without stalling all work

# Related Code Files

## Files to modify
- None in this planning task

## Files to create later
- harness files from prior phases

## Files to delete
- None

# Implementation Steps

1. Build harness files in additive order.
2. Run dry-run using a sample phase from current product plan.
3. Adjust prompts for any overlap/confusion.
4. Start real usage on one phase.
5. Measure cycle time, failed handoffs, QA escapes.

# Todo List

- [ ] Define migration order
- [ ] Define backwards compatibility stance
- [ ] Define rollback steps
- [ ] Define adoption metrics

# Success Criteria

- Pilot phase completes with explicit handoffs and one QA gate pass
- No file ownership collision in pilot
- Tracking docs updated exactly once after pilot pass
- Harness can be disabled without harming product plan

# Risk Assessment

- Medium: over-designed harness slows MVP -> mitigate by piloting with 5 roles only
- Medium: prompt drift across files -> mitigate by central workflow summary in `CLAUDE.md`
- Low: rollback ambiguity -> mitigate by additive, doc-first rollout

# Security Considerations

- Harness prompts must state secret handling and least-privilege ownership
- QA gate must confirm no credentials committed during rollout

# Next Steps

- Implement harness docs and agent prompts per this plan
