---
title: Hybrid Interview Copilot Implementation Plan
status: completed
createdAt: 2026-04-23
updatedAt: 2026-04-23
blockedBy: []
blocks: []
---

# Plan Overview

Source brief: `interview-copilot-brief6.md`
Goal: implement hybrid local-agent + web overlay interview copilot with low-latency streaming and local key custody.

## Phases

1. **Phase 01 — Bootstrap repository and architecture docs** (`phase-01-bootstrap-repository-and-architecture-docs.md`) — completed
2. **Phase 02 — Define shared realtime protocol and config contracts** (`phase-02-define-shared-realtime-protocol-and-config-contracts.md`) — completed
3. **Phase 03 — Build local agent foundation (audio + websocket)** (`phase-03-build-local-agent-foundation-audio-and-websocket.md`) — completed
4. **Phase 04 — Implement ASR, language, intent pipeline** (`phase-04-implement-asr-language-intent-pipeline.md`) — completed
5. **Phase 05 — Implement answer generation and QC prompt system** (`phase-05-implement-answer-generation-and-qc-prompt-system.md`) — completed
6. **Phase 06 — Build web overlay UI realtime client** (`phase-06-build-web-overlay-ui-realtime-client.md`) — completed
7. **Phase 07 — Integrate end-to-end, harden, validate, and package** (`phase-07-integrate-end-to-end-harden-validate-and-package.md`) — completed

## Dependencies

- P01 must finish before all phases (repo/docs baseline)
- P02 blocks P03/P06 (shared event schema)
- P03 blocks P04/P05 (runtime agent plumbing)
- P04 feeds P05 inputs
- P05 + P06 block P07 integration

## Key Non-Functional Targets

- End-to-end response target: `<= 1.5s` median
- No API keys in web client
- Default zero-storage behavior
- Fallback ASR path when cloud ASR unavailable

## Execution Notes

- Keep implementation files under ~200 lines by modular decomposition.
- Prefer simple modules over deep abstractions (YAGNI/KISS/DRY).
- Update `docs/` after major milestones.
