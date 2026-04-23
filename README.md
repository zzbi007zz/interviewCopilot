# interviewCopilot

Hybrid interview copilot project based on `interview-copilot-brief6.md`.

## Planning

- Active product plan: `plans/260423-1735-hybrid-interview-copilot-implementation/plan.md`
- Harness setup plan: `plans/260423-1009-project-harness-agent-team/plan.md`

## Phase 01 Baseline Structure

- `agent/` local runtime components (scaffold)
- `web/` React/Next.js overlay client (scaffold)
- `shared/` cross-runtime contracts (scaffold)
- `scripts/` setup and utility scripts (scaffold)

## Run Instructions (Current Baseline)

1. Copy `.env.example` to `.env` for local development.
2. Fill local provider keys only in `.env` (never commit secrets).
3. Use the active plan to implement the next phase scope.
4. Keep phase gate flow enforced: implementation -> QA PASS -> tracking update.

Note: runnable agent/web application commands are introduced in later phases when runtime code is implemented.

## Delivery Harness

This repo uses a dedicated team harness for phased implementation:

- frontend-implementer
- backend-api-implementer
- blocker-researcher
- qa-gate-verifier
- project-tracker
- team-orchestrator

Orchestrator skill: `interview-copilot-team-orchestrator`.

## Gate Rules

No phase progression without:

1. QA PASS report in `plans/reports/`
2. Tracking docs update in `docs/`

## Tracking Docs

- `docs/development-roadmap.md`
- `docs/project-changelog.md`
- `docs/system-architecture.md`
- `docs/project-roadmap.md`
