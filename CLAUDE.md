# CLAUDE.md

## Harness: interview-copilot-delivery-team

**Goal:** Run feature delivery with a fixed specialist team (frontend, backend, blocker research, QA gate, tracking updates) so each phase ships with verifiable quality and traceable progress.

**Trigger:** For implementation/fix/update requests in this repo, use `interview-copilot-team-orchestrator` skill. Direct Q&A without execution can be answered directly.

## Team Flow

1. Scope + contract lock
2. Frontend and backend implementation (parallel only when ownership is disjoint)
3. Research on blocker (when needed)
4. QA gate verification (mandatory)
5. Tracking docs update (mandatory after QA PASS)
6. Open next phase

## Mandatory Gate Rule

No phase promotion without:

- QA gate report with explicit PASS
- tracking docs update completion

Gate sequence is strict:

`implementation -> QA PASS -> tracking update -> next phase`

## Skill and Agent Locations

- Agents: `./.claude/agents/`
- Skills: `./.claude/skills/`
- Tracking docs: `./docs/`
- Reports: `./plans/reports/`

## Harness Change History

| Date | Change | Target | Reason |
|---|---|---|---|
| 2026-04-23 | Initial harness setup for frontend/backend/researcher/QA/tracker team | `.claude/agents/*`, `.claude/skills/*`, `CLAUDE.md` | Enable controlled phased delivery with QA gate and tracking discipline |
