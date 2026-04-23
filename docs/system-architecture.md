# System Architecture

## Source Architecture

Primary source: `interview-copilot-brief6.md`.

Core runtime pipeline:

`Audio Capture -> Streaming ASR -> Language/Intent -> Answer Generation -> Overlay UI`

## Runtime Boundaries

- `agent/`: local runtime for audio capture, provider integrations, and local key custody.
- `shared/`: cross-runtime contracts and realtime event schemas.
- `web/`: React/Next.js overlay client that consumes shared contracts and renders assistant output.
- `scripts/`: setup and utility scripts for local workflows.

## Trust and Security Boundaries

- Provider keys must stay in local agent environment (`.env`), never in web/client code.
- Browser/UI receives processed events and responses, not raw provider secrets.
- Zero-storage mode is default baseline unless intentionally changed.

## Phase 01 Baseline State

- Baseline docs and scaffold directories exist for `agent/`, `web/`, `shared/`, and `scripts/`.
- `.env.example` defines the initial local configuration surface for provider keys and websocket host/port settings.
- Runtime implementation (agent/web executable components) begins in later phases.

## Delivery Governance Architecture

This repository uses a team-based delivery harness:

- Frontend implementer (React/Next.js scope)
- Backend API implementer (service/API scope)
- Blocker researcher (on-demand investigation)
- QA gate verifier (incremental phase gate)
- Project tracker (roadmap/changelog updates)
- Team orchestrator (phase control)

Governance flow:

`scope lock -> implementation -> QA gate -> tracking update -> next phase`

## Phase 07 Runtime Hardening State

The current validated runtime contract now includes two hardening additions:

- `health.diagnostics` event for local runtime snapshot visibility
- explicit error taxonomy with stable `code`, `stage`, and `retryable` fields

### Realtime event flow

`status.update -> health.diagnostics -> transcript.final -> intent.detected -> answer.generated`

Error/fallback path can additionally emit:

`error -> health.diagnostics`

### Diagnostics payload purpose

The diagnostics event carries only operational snapshot data safe for the localhost UI:

- session id and startup time
- current runtime state
- active ASR provider
- fallback active flag
- audio readiness flag
- counts for partial/final/answer/error events
- last error code/stage/retryable summary

It does not carry provider secrets, prompts, or stack traces.

### Error taxonomy boundary

Client-safe error taxonomy is centralized in `agent/message_router.py` and currently covers:

- primary ASR timeout
- fallback ASR unavailable
- pipeline failure
- audio device unavailable
- startup failure
- answer generation failure

This keeps browser-visible failures stable and suitable for diagnostics without exposing internal exception details.

## Quality Boundary

- QA verifies boundary coherence between backend contracts and frontend consumers.
- No phase can be marked complete without explicit PASS report.
