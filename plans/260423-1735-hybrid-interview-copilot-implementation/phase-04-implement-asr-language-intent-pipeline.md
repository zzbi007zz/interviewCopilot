# Phase 04 — Implement ASR, language, intent pipeline

## Context Links
- Plan overview: `./plan.md`
- Depends on: `phase-03-build-local-agent-foundation-audio-and-websocket.md`

## Overview
- Priority: High
- Status: Completed
- Purpose: Convert audio stream into structured transcript + language + intent outputs.

## Key Insights
- Keep ASR provider behind interface for cloud/local fallback.
- Interim transcripts are needed for latency; finals used for answer generation trigger.

## Requirements
- Functional:
  1. Integrate streaming cloud ASR (Deepgram or equivalent).
  2. Add local fallback ASR adapter.
  3. Add language detection and optional translation layer.
  4. Add intent classifier (rule-first, LLM-assist fallback).
- Non-functional:
  1. No blocking operations on realtime path.
  2. Clear provider timeout/failure handling.

## Architecture
- `agent/asr-provider.py` interface
- `agent/asr-deepgram.py` primary provider
- `agent/asr-local-fallback.py` fallback provider
- `agent/language-and-intent-pipeline.py` processing chain

## Related Code Files
- `agent/asr-provider.py`
- `agent/asr-deepgram.py`
- `agent/asr-local-fallback.py`
- `agent/language-and-intent-pipeline.py`
- `agent/message-router.py`

## Implementation Steps
1. Implement ASR provider interface and cloud adapter.
2. Add fallback adapter and failover policy.
3. Add language detection and translation toggles.
4. Add intent extractor and emit protocol events.

## Todo List
- [x] Integrate streaming ASR primary provider
- [x] Implement fallback provider and failover
- [x] Implement language detect/translate path
- [x] Implement intent extraction and event emission

## Success Criteria
- Agent emits transcript partial/final + intent events from real audio.
- Fallback path activates when primary ASR unavailable.

## Risk Assessment
- Risk: Provider SDK instability under long sessions.
- Mitigation: reconnect strategy + bounded retries.

## Security Considerations
- Redact transcript content from error logs by default.

## Next Steps
- Feed final intent/question events into answer generation.
