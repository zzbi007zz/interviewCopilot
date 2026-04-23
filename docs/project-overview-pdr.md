# Project Overview (PDR)

## Product

Cross-platform Interview Copilot with hybrid architecture:

- local audio capture agent
- streaming ASR and language/intent pipeline
- low-latency answer generation
- floating web overlay UI

## Goals

1. Keep end-to-end answer latency near 1.5s median.
2. Keep API keys local to agent runtime.
3. Support default zero-storage behavior.
4. Provide concise EN/VI interview response options.

## Scope Boundaries

- In scope: local agent pipeline, web overlay client, realtime messaging contracts, QA gate workflow.
- Out of scope for initial phases: production-grade account system, long-term transcript storage, analytics pipeline.

## Phase Baseline

Current verified baseline:

- Phase 01 bootstrap is complete
- Repository includes baseline docs, scaffold directories, and local env template
- Runnable runtime components are deferred to later phases

Source implementation plan:

- `plans/260423-1735-hybrid-interview-copilot-implementation/plan.md`

Phase progression policy:

- `implementation -> QA PASS -> tracking update -> next phase`
