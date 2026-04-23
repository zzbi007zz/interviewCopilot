# Phase 07 implementation plan — integrate, harden, validate, package

## Scope lock
Ship one production-like local flow only: `audio -> ASR -> language/intent -> answer -> websocket -> overlay`. No new product features. Only integration, hardening, validation, packaging, docs.

## Execution checklist
- [ ] Freeze Phase 07 scope to integration + hardening only
- [ ] Verify dependency inputs from phases 03/04/05/06 still compile together
- [ ] Add backend integration coverage for final transcript -> answer -> websocket broadcast
- [ ] Add web integration coverage for websocket event intake -> overlay render state
- [ ] Add shared contract validation coverage for full event envelopes used in E2E path
- [ ] Add health/diagnostic surface for runtime readiness and degraded mode visibility
- [ ] Add startup/preflight scripts for local env, agent, web, and audio prereqs
- [ ] Run local end-to-end smoke path with realistic meeting audio fixture
- [ ] Measure latency; record median and failure cases against `<=1.5s` target
- [ ] Run mandatory QA gate and get explicit PASS
- [ ] Only after QA PASS, update tracking docs in `docs/`

## Data flow
1. Audio enters `agent/audio_capture.py`
2. Transcript leaves ASR modules (`agent/asr_deepgram.py` or `agent/asr_local_fallback.py`) via `agent/asr_provider.py`
3. Transcript transforms in `agent/language_and_intent_pipeline.py`
4. Final transcript + intent feed `agent/answer_orchestrator.py`
5. Normalized answer event emits through `agent/message_router.py` and `agent/ws_hub.py`
6. Web client ingests via `web/src/lib/protocol.ts` and websocket hooks/store
7. Overlay renders final state in UI components
8. Diagnostics exit via health/status endpoint or event surface and docs/test reports

## File-level scope

### Backend
Modify only files needed for integration seam, diagnostics, and packaging-safe runtime behavior:
- `/Users/february10/Documents/interviewCopilot/agent/main.py`
- `/Users/february10/Documents/interviewCopilot/agent/message_router.py`
- `/Users/february10/Documents/interviewCopilot/agent/ws_hub.py`
- `/Users/february10/Documents/interviewCopilot/agent/runtime_state.py`
- `/Users/february10/Documents/interviewCopilot/agent/config.py`
- `/Users/february10/Documents/interviewCopilot/agent/audio_capture.py`
- `/Users/february10/Documents/interviewCopilot/agent/asr_provider.py`
- `/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py`
- `/Users/february10/Documents/interviewCopilot/agent/asr_local_fallback.py`
- `/Users/february10/Documents/interviewCopilot/agent/language_and_intent_pipeline.py`
- `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py`
- `/Users/february10/Documents/interviewCopilot/agent/answer_client.py`
- `/Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py`
- `/Users/february10/Documents/interviewCopilot/agent/answer_fallback.py`

### Web
Keep scope to realtime consumption, degraded-state visibility, and E2E-safe rendering only:
- `/Users/february10/Documents/interviewCopilot/web/src/app.tsx`
- `/Users/february10/Documents/interviewCopilot/web/src/components/floating-overlay-panel.tsx`
- `/Users/february10/Documents/interviewCopilot/web/src/lib/protocol.ts`
- `/Users/february10/Documents/interviewCopilot/web/src/lib/local-agent-url.ts`
- existing websocket/store modules under `web/src/` tied to local agent session state
- tests under `/Users/february10/Documents/interviewCopilot/web/src/test/`

### Shared
Contract-first. Additive only. No breaking schema rename:
- `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts`
- `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.js`
- `/Users/february10/Documents/interviewCopilot/shared/protocol-fixtures/realtime-events-v1.json`
- `/Users/february10/Documents/interviewCopilot/shared/config-contracts.md` only if config surface changes materially

### Scripts
Create practical local packaging/startup/preflight entrypoints:
- `/Users/february10/Documents/interviewCopilot/scripts/start-local-dev.sh`
- `/Users/february10/Documents/interviewCopilot/scripts/check-system-audio-prereqs.sh`
- optional one-shot smoke runner only if reused by QA; otherwise avoid

### Docs
Update only after QA PASS:
- `/Users/february10/Documents/interviewCopilot/README.md`
- `/Users/february10/Documents/interviewCopilot/docs/deployment-guide.md`
- `/Users/february10/Documents/interviewCopilot/docs/system-architecture.md`
- `/Users/february10/Documents/interviewCopilot/docs/development-roadmap.md`
- `/Users/february10/Documents/interviewCopilot/docs/project-changelog.md`
- `/Users/february10/Documents/interviewCopilot/docs/project-roadmap.md` if milestone state changes need sync

## Dependency graph
- Phase 03 local runtime is prerequisite for health/preflight and websocket diagnostics
- Phase 04 transcript + intent output is prerequisite for backend E2E assertions
- Phase 05 answer generation is prerequisite for final response and fallback-path validation
- Phase 06 overlay realtime client is prerequisite for render-path validation
- Shared contract updates block both backend emitter and web consumer tests
- QA gate blocks tracking docs update
- Tracking docs update blocks opening next phase / packaging signoff

## File ownership / parallel safety
- Backend stream owns only `agent/*` and backend integration tests
- Frontend stream owns only `web/src/**` and web tests
- Shared/schema stream owns only `shared/*`
- Packaging/docs stream owns only `scripts/*`, `README.md`, `docs/*`
- Avoid parallel edits to `web/src/lib/protocol.ts` and `shared/realtime-event-contracts.ts` at same time; shared lands first
- Avoid parallel edits to `agent/main.py` and startup scripts until runtime entrypoints are locked

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---:|---|
| Event contract drift between backend and web | Medium | High | Contract fixtures + validator tests + additive-only changes |
| Environment-specific audio failures | High | High | Preflight script + troubleshooting matrix + explicit health state |
| Latency target missed in real local run | Medium | High | Measure stage timings, use fallback path, bound provider calls, no new features |
| Duplicate or missing final answer events | Medium | High | Integration test around final transcript dedupe and one-answer-per-final invariant |
| Secret leakage in diagnostics/logs | Low | High | Redact provider errors, localhost-only defaults, no key/value echo |
| Packaging scripts drift from real commands | Medium | Medium | Reuse tested commands from QA smoke flow, one canonical start path |

## Backwards compatibility
- Keep localhost-first architecture unchanged
- Keep existing event names unchanged; additive metadata only
- Keep zero-storage default unchanged
- Existing single-module startup remains usable until new scripts proven stable
- No persisted data migration expected; migration path is command-path update only

## Test matrix

### Unit
- backend: parser/fallback/diagnostic helpers/config parsing
- shared: event schema validators and fixtures
- web: protocol parser, store reducers, overlay degraded-state rendering

### Integration
- backend: final transcript -> intent -> answer -> websocket event order
- backend: provider failure -> fallback answer + safe diagnostics
- web: websocket envelope -> store update -> visible overlay state
- scripts: preflight returns actionable failures for missing env/audio prereqs

### End-to-end
- local smoke run with realistic audio fixture
- no-provider / fallback path run
- valid-provider path run if local keys available
- latency capture: median response `<=1.5s` target in expected local env
- packaging path: fresh setup from `.env.example` + scripts succeeds

## Rollback plan
- Revert startup scripts first if packaging path unstable
- Revert diagnostics additions if they break runtime boot, keep core answer path intact
- Revert additive shared contract fields if web consumer mismatch appears
- Revert E2E wiring in `agent/main.py` / `message_router.py` only if it destabilizes phase 05/06 behavior
- Since no DB/storage migration exists, rollback is code-only and low blast radius

## Mandatory gate sequence
1. Implementation complete on owned files
2. Compile/typecheck/unit+integration tests green
3. QA gate verifier runs full phase validation
4. Explicit QA report with PASS saved in `/Users/february10/Documents/interviewCopilot/plans/reports/`
5. Project tracker updates `docs/development-roadmap.md` and companion docs
6. Only then mark Phase 07 complete / open next phase

## First concrete implementation action
Start with shared + backend contract seam, not scripts/docs.

Immediate first step:
1. Read current websocket emit path in `/Users/february10/Documents/interviewCopilot/agent/message_router.py`, `/Users/february10/Documents/interviewCopilot/agent/ws_hub.py`, and `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts`
2. Lock the exact end-to-end event list and payloads for the happy path plus fallback/health path
3. Write failing integration test that asserts one final transcript produces ordered events consumable by web overlay

Reason: this de-risks the highest-impact boundary first and prevents scripts/docs from documenting unstable behavior.

## Success criteria
- Observable full local flow from audio input to overlay answer render
- Observable health/readiness surface reports degraded states without secret leakage
- Measured latency report exists with median result and environment notes
- Canonical startup/preflight scripts work on clean local setup
- QA report explicitly PASS before any tracking doc update

## Unresolved questions
- Which realistic audio fixture should be canonical for latency and smoke verification?
- Should diagnostics be HTTP health only, websocket status event only, or both? Minimal recommendation: one health endpoint plus additive status event only if already cheap.
