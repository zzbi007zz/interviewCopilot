---
name: interview-copilot-team-orchestrator
description: "Orchestrate this project with a dedicated delivery team: frontend (React/Next.js), backend API, blocker researcher, QA phase gate, and project tracking updates. Use this for implement/build/fix/update requests, phase reruns, partial reruns, and result improvement requests."
---

# Interview Copilot Team Orchestrator

Use this orchestrator for all non-trivial implementation work in this repository.

## Execution Mode

Agent-team workflow with phased gates:

1. Scope and contract lock
2. Frontend + backend implementation (parallel when safe)
3. Blocker research (on demand)
4. QA gate (mandatory)
5. Tracking docs update (mandatory)
6. Next phase decision

## Team Roster

| Role | subagent_type | model | Responsibility |
|---|---|---|---|
| Orchestrator | team-orchestrator | opus | Phase control, routing, gate enforcement |
| Frontend | frontend-implementer | opus | React/Next.js implementation |
| Backend | backend-api-implementer | opus | API/service implementation |
| Research | blocker-researcher | opus | Blocker investigation and decision memo |
| QA | qa-gate-verifier | opus | Incremental pass/fail gate decision |
| Tracker | project-tracker | opus | Roadmap/changelog/architecture updates |

## Required Dispatch Packet

Every agent dispatch must include:

- Task description and expected status contract (`DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, `NEEDS_CONTEXT`)
- Explicit file ownership boundaries
- Acceptance criteria
- Work context paths:
  - `Work context: /Users/february10/Documents/interviewCopilot`
  - `Reports: /Users/february10/Documents/interviewCopilot/plans/reports/`
  - `Plans: /Users/february10/Documents/interviewCopilot/plans/`

## Workflow

### Phase 0 — Context Check

1. Determine target phase from user request and active plan.
2. Check workspace state:
   - `_workspace/{phase}` absent -> initial run.
   - `_workspace/{phase}` present + partial fix request -> partial rerun.
   - `_workspace/{phase}` present + new scope -> archive previous workspace then create fresh scope package.

### Phase 1 — Scope + Contract Lock

1. Define acceptance criteria.
2. Lock file ownership for FE/BE.
3. If FE+BE integration exists, create contract note:
   - `_workspace/{phase}/contracts/api-contract.md`

### Phase 2 — Implementation

1. Dispatch frontend and backend in parallel only if ownership does not overlap.
2. Require each to produce handoff artifacts:
   - `_workspace/{phase}/handoff/frontend.md`
   - `_workspace/{phase}/handoff/backend.md`

### Phase 3 — Blocker Handling (Conditional)

Trigger blocker-researcher when:

- Any implementer returns `BLOCKED`
- Any implementer returns `NEEDS_CONTEXT` with dependency ambiguity
- Repeated failed approach without clear next path

Output required:

- `_workspace/{phase}/research/blocker-{slug}.md`
- one recommended option + risk/rollback note

### Phase 4 — Handoff Completeness Check

Run handoff checklist before QA:

- frontend handoff exists and includes evidence
- backend handoff exists and includes evidence
- contract note updated when API changed

### Phase 5 — QA Gate (Mandatory)

Dispatch `qa-gate-verifier` with phase acceptance criteria and handoff artifacts.

Output must be:

- `plans/reports/qa-gate-{date}-{phase}.md`
- explicit gate decision line: `PASS` or `FAIL`

Rules:

- FAIL -> phase remains open, return fix list to owners, rerun QA.
- PASS -> proceed to tracking update.

### Phase 6 — Tracking Update (Mandatory)

After QA PASS, dispatch `project-tracker` to update:

- `docs/development-roadmap.md`
- `docs/project-changelog.md`
- `docs/system-architecture.md` only if structural change occurred
- `CLAUDE.md` change history only when harness configuration changed

### Phase 7 — Phase Close

Return concise closure summary:

- implemented scope
- QA result
- docs updated
- next phase readiness

## Data Handoff Schema

### Frontend handoff

- scope summary
- changed files
- acceptance checklist mapping
- test/build evidence
- known risks

### Backend handoff

- route/service summary
- request/response examples
- changed files
- test evidence
- rollback note

### QA gate report

- scope
- checks run
- evidence links
- failed items (if any)
- risk rating
- gate decision
- unblock recommendation

## Failure Policy

- Missing context -> request only required context and retry once.
- Repeated blocker -> escalate with options to user.
- Never open next phase before QA PASS and tracking update completion.

## Test Scenarios

### Normal Flow

1. Dispatch FE+BE for phase.
2. Validate handoff completeness.
3. QA returns PASS.
4. Tracker updates roadmap/changelog.
5. Mark phase complete.

### Blocker Flow

1. Backend returns BLOCKED on external dependency.
2. Researcher returns decision memo.
3. Backend applies chosen option.
4. QA runs and returns PASS/FAIL.
5. Continue only on PASS.

### QA Fail Flow

1. QA finds contract mismatch.
2. Return precise fix list to FE/BE owner.
3. Rerun only affected agent.
4. Re-run QA gate.
