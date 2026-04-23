---
title: "Project harness agent team plan"
description: "Setup plan for Claude harness, agent team orchestration, QA gates, and phase tracking."
status: pending
priority: P1
effort: 8h
branch: main
tags: [planning, harness, agents, qa, tracking]
created: 2026-04-23
---

# Plan Overview

Goal: add a reusable project harness for this repo so frontend, backend, researcher, QA, and project-tracking roles can work in a controlled phase-by-phase flow.

## Recommended pattern

- Pattern: controller-led sequential pipeline with bounded parallel execution inside each phase
- Mode: `Plan -> Research (parallel if blocked) -> Impl (frontend/backend parallel) -> QA gate -> Tracking update -> Next phase`
- Why: keeps shared files stable, enforces QA before progression, preserves simple ownership

## Phases

1. [Phase 01 — define harness skeleton and ownership](./phase-01-define-harness-skeleton-and-ownership.md)
2. [Phase 02 — design execution flow and QA gate rules](./phase-02-design-execution-flow-and-qa-gate-rules.md)
3. [Phase 03 — define tracking docs and update protocol](./phase-03-define-tracking-docs-and-update-protocol.md)
4. [Phase 04 — rollout, validation, and migration path](./phase-04-rollout-validation-and-migration-path.md)

## Dependency graph

- P01 blocks all later phases
- P02 depends on P01, blocks P03/P04
- P03 depends on P02
- P04 depends on P02 + P03

## Data flows

- User request -> lead/controller agent -> phase task dispatch
- Feature spec -> frontend/backend agents -> code/test evidence -> QA gate agent
- Blocker report -> researcher agent -> decision memo -> lead/controller
- Phase result -> project-tracker agent -> `docs/development-roadmap.md` + `docs/project-changelog.md`
- Harness config/docs -> future subagents via `CLAUDE.md` + `.claude/agents/*` + `.claude/skills/*`

## File ownership

- Harness meta only: `.claude/agents/*`, `.claude/skills/*`, `CLAUDE.md`
- Tracking only: `docs/development-roadmap.md`, `docs/project-changelog.md`, optional `docs/system-architecture.md`
- No parallel phase edits to same file

## Success criteria

- Clear role files defined for 5 roles
- QA gate blocks phase advancement until explicit pass criteria met
- Tracking docs update after every completed phase
- Backwards-compatible adoption path from no-harness state
- Team can execute without touching same file in parallel
