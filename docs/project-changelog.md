# Project Changelog

## 2026-04-23

### Added

- Initial delivery harness structure under `./.claude/agents/` and `./.claude/skills/`.
- Team roles for frontend, backend, blocker research, QA gate verification, project tracking, and orchestration.
- Orchestrator skill enforcing strict sequence: implementation -> QA PASS -> tracking update -> next phase.
- Baseline tracking docs in `./docs/`.

### Validated

- Dry-run QA gate passed for phase `01-bootstrap-repository-and-architecture-docs` (`plans/reports/qa-gate-2026-04-23-phase-01-bootstrap-dry-run.md`).
- Tracking update flow executed after QA PASS (roadmap/changelog updated as required by harness gate).
- Implementation QA gate passed for phase `01-bootstrap-repository-and-architecture-docs` (`plans/reports/qa-gate-2026-04-23-phase-01-bootstrap-implementation.md`).

### Changed

- Added baseline scaffold directories: `agent/`, `web/`, `shared/`, `scripts/`.
- Added required phase-01 documentation files:
  - `docs/project-overview-pdr.md`
  - `docs/code-standards.md`
  - `docs/codebase-summary.md`
  - `docs/design-guidelines.md`
  - `docs/deployment-guide.md`
  - `docs/project-roadmap.md`
- Added local env baseline: `.env.example`.
- Updated `README.md` with baseline structure and current run instructions.
- Updated `docs/system-architecture.md` with runtime pipeline and trust boundaries.
- Reconciled phase-tracking statuses in product plan and phase-01 details.

### Phase 02

#### Added

- Shared realtime protocol contract implementation: `shared/realtime-event-contracts.ts`.
- Web adapter contract helper: `web/src/lib/protocol.ts`.
- Agent startup config contract and validation: `agent/config.py`.
- Config contract documentation: `shared/config-contracts.md`.
- Event fixture set for protocol conformance checks: `shared/protocol-fixtures/realtime-events-v1.json`.

#### Security

- Protocol rules explicitly avoid secret propagation in event payloads.
- Config contracts keep provider keys local to agent runtime.
- Added websocket boundary parser improvements for both single event and envelope payload handling with parse error classification.
- Hardened metadata and error message validation to reduce secret/stack leakage risk in event payloads.

### Validated (Phase 02)

- QA gate PASS: `plans/reports/qa-gate-2026-04-23-phase-02-protocol-contracts.md`.
- Protocol fixtures aligned with runtime contract validators.
- Python config validation enforces strict boolean parsing for `ZERO_STORAGE_MODE`.

### Phase 03

#### Added

- Local runtime entrypoint and lifecycle bootstrap: `agent/main.py`.
- Runtime state module for transient session/status tracking: `agent/runtime_state.py`.
- Websocket hub foundation for local client sessions and broadcasts: `agent/ws_hub.py`.
- Audio capture abstraction with probe/start/stop hooks: `agent/audio_capture.py`.
- Agent dependency baseline: `agent/requirements.txt`.
- Extended runtime config surface in `.env.example`:
  - `AUDIO_DEVICE_NAME`
  - `AUDIO_SAMPLE_RATE`
  - `AUDIO_CHUNK_MS`

#### Security

- Enforced local-only websocket host policy in startup validation (`127.0.0.1` or `localhost`).
- Added websocket peer + origin guards and hardened origin parsing against prefix-bypass patterns.
- Preserved contract rule: secrets remain local to agent runtime.

### Validated (Phase 03)

- QA gate PASS: `plans/reports/qa-gate-2026-04-23-phase-03-local-agent-foundation.md`.
- Tester gate PASS for config/lifecycle/protocol emission checks.
- Code-review gate PASS after websocket security and resilience hardening.

### Phase 04

#### Added

- ASR provider contract module: `agent/asr_provider.py`.
- Primary ASR adapter baseline: `agent/asr_deepgram.py`.
- Local fallback ASR adapter baseline: `agent/asr_local_fallback.py`.
- Language + intent processing pipeline: `agent/language_and_intent_pipeline.py`.
- ASR routing integration for transcript/intent event emission: `agent/message_router.py`.
- New QA gate report for phase close: `plans/reports/qa-gate-2026-04-23-phase-04-asr-language-intent-pipeline.md`.

#### Validated

- Initial tester gate PASS: `plans/reports/tester-2026-04-23-phase-04-asr-language-intent.md`.
- Initial code-review gate FAIL addressed by targeted fixes.
- Rerun code-review gate PASS: `plans/reports/code-reviewer-2026-04-23-phase-04-asr-language-intent-rerun.md`.
- Rerun tester gate PASS: `plans/reports/tester-2026-04-23-phase-04-asr-language-intent-rerun.md`.
- QA gate PASS: `plans/reports/qa-gate-2026-04-23-phase-04-asr-language-intent-pipeline.md`.

#### Changed

- Hardened startup config parsing in `agent/config.py` with env-specific strict bool error messages and non-empty `AUDIO_DEVICE_NAME` enforcement.
- Updated primary timeout semantics in `agent/asr_deepgram.py` to use activity-based timing.
- Added bounded duplicate suppression window in `agent/runtime_state.py` to avoid session-wide false drops.
- Serialized ASR result handling in `agent/main.py` with queue worker to reduce callback race/order risks.
- Added buffered audio replay on fallback switch in `agent/main.py` to reduce transcript loss at failover boundary.
- Redacted startup status error message in `agent/main.py` to avoid exposing internal exception details.
- Synced Phase 04 config surface in `.env.example` and `shared/config-contracts.md`.

### Phase 05

#### Added

- Anthropic answer provider wrapper with timeout/max-token guards: `agent/answer_client.py`.
- Deterministic QC prompt builder for EN/VI output shaping: `agent/qc_prompt_template.py`.
- Strict Option A/Option B answer parser: `agent/answer_output_parser.py`.
- Deterministic fallback answer templates for EN/VI + intent category: `agent/answer_fallback.py`.
- Answer orchestration module combining prompt/client/parser/fallback: `agent/answer_orchestrator.py`.
- Targeted unit tests for parser strictness and language normalization: `tests/test_phase_05_answer_modules.py`.
- Phase 05 QA gate report: `plans/reports/qa-gate-2026-04-23-phase-05-answer-generation-and-qc-prompt-system.md`.

#### Validated

- Initial tester gate identified missing formal tests and was addressed.
- Initial code-review gate flagged language+parser issues and was addressed.
- Tester final PASS: `plans/reports/tester-2026-04-23-phase-05-answer-generation-and-qc-final.md`.
- Code-review final PASS: `plans/reports/code-reviewer-2026-04-23-phase-05-answer-generation-and-qc-final.md`.
- QA gate PASS: `plans/reports/qa-gate-2026-04-23-phase-05-answer-generation-and-qc-prompt-system.md`.

#### Changed

- Extended runtime config in `agent/config.py` with:
  - `ANSWER_MAX_TOKENS`
  - `ANSWER_PROVIDER_TIMEOUT_MS`
- Synced answer config vars in `.env.example` and `shared/config-contracts.md`.
- Expanded `answer.generated` event contract in `shared/realtime-event-contracts.ts` with:
  - `sourceText`
  - `questionType`
  - `fallbackUsed`
  - `qcStatus`
  - language enforcement to `en|vi`
- Updated fixture payload in `shared/protocol-fixtures/realtime-events-v1.json` to match expanded answer event schema.
- Integrated answer generation in `agent/message_router.py` so final transcript path emits `answer.generated` after `intent.detected`.

### Phase 06

#### Added

- Web app runtime scaffold + Vite build pipeline:
  - `web/package.json`
  - `web/tsconfig.json`
  - `web/vite.config.ts`
  - `web/index.html`
  - `web/src/main.tsx`
  - `web/src/app.tsx`
- Realtime UI state and websocket integration modules:
  - `web/src/hooks/use-local-agent-websocket.ts`
  - `web/src/state/realtime-session-store.ts`
  - `web/src/lib/local-agent-url.ts`
  - `web/src/components/floating-overlay-panel.tsx`
  - `web/src/styles/overlay.css`
- Phase 06 test coverage files:
  - `web/src/test/realtime-session-store.test.ts`
  - `web/src/test/use-local-agent-websocket.test.tsx`
  - `web/src/test/floating-overlay-panel.test.tsx`
- Phase 06 QA gate report:
  - `plans/reports/qa-gate-2026-04-23-phase-06-web-overlay-realtime-client.md`

#### Validated

- Build PASS for web client: `npm run build --prefix web`.
- Realtime reducer and overlay rendering tests PASS.
- Websocket reconnect/manual-disconnect behavior validated with documented test-environment limitation.
- QA gate PASS: `plans/reports/qa-gate-2026-04-23-phase-06-web-overlay-realtime-client.md`.

#### Changed

- Added stale-answer guard in `web/src/state/realtime-session-store.ts` to prevent old `answer.generated` payload from overriding newer question state.
- Added localhost-only websocket URL constraint in `web/src/lib/local-agent-url.ts`.
- Updated websocket close/reconnect flow in `web/src/hooks/use-local-agent-websocket.ts` to separate manual disconnect from reconnect scheduling path.

### Phase 07

#### Added

- Runtime diagnostics snapshots via `health.diagnostics` realtime event in `shared/realtime-event-contracts.ts`.
- Diagnostics state tracking in `agent/runtime_state.py` for transcript, answer, and error counters.
- Explicit stage-based error taxonomy in `agent/message_router.py` and ASR provider error results.
- Phase 07 QA gate report: `plans/reports/qa-gate-2026-04-23-phase-07-integrate-end-to-end-harden-validate-and-package.md`.

#### Validated

- Python validation PASS: `python3 -m unittest /Users/february10/Documents/interviewCopilot/tests/test_phase_05_answer_modules.py /Users/february10/Documents/interviewCopilot/tests/test_phase_07_agent_websocket_flow.py`.
- Web validation PASS: `npm test --prefix "/Users/february10/Documents/interviewCopilot/web"`.
- Web production build PASS: `npm run build --prefix "/Users/february10/Documents/interviewCopilot/web"`.
- QA gate PASS: `plans/reports/qa-gate-2026-04-23-phase-07-integrate-end-to-end-harden-validate-and-package.md`.
- Local baseline latency measurement PASS with 25 samples and median `0.020 ms` for implemented transcript-to-answer routing path.

#### Changed

- Updated `agent/main.py` to emit health diagnostics snapshots at startup, audio-ready, fallback activation, and error boundaries.
- Updated `web/src/state/realtime-session-store.ts` to store diagnostics provider/fallback/error snapshot data.
- Extended `shared/realtime-event-contracts.ts` to accept `health.diagnostics` events and error `stage` metadata.
- Expanded `tests/test_phase_07_agent_websocket_flow.py` and `web/src/test/realtime-session-store.test.ts` to cover taxonomy and diagnostics handling.
- Confirmed local packaging path via `scripts/start-local-dev.sh` and `scripts/check-system-audio-prereqs.sh` for localhost-only startup flow.

#### Security

- Preserved localhost-only websocket posture.
- Preserved no-secret/no-stack-trace exposure in client-facing error payloads.
- Preserved local key custody; no provider secret moved into browser code.

### Notes

- This changelog tracks QA-approved phase outcomes for product work.
- Harness bootstrap entry is recorded as governance setup.
