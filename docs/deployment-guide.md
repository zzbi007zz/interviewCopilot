# Deployment Guide

## Current Phase Reality

Phase 07 is complete for the current local baseline. The repository now contains a runnable localhost-only agent + web overlay flow with startup and preflight scripts.

## Local Development / Startup

1. Copy `/Users/february10/Documents/interviewCopilot/.env.example` to local `.env`.
2. Fill provider keys only in local `.env`.
3. Run preflight checks:

```bash
/Users/february10/Documents/interviewCopilot/scripts/check-system-audio-prereqs.sh
```

4. Start local agent + overlay together:

```bash
/Users/february10/Documents/interviewCopilot/scripts/start-local-dev.sh
```

5. Open `http://127.0.0.1:5173`.

## Runtime Notes

- Agent websocket host must remain `127.0.0.1` or `localhost`.
- Web overlay connects only to localhost websocket endpoints.
- If no live answer-provider key is configured, the current baseline uses deterministic fallback answer generation.
- Diagnostics snapshots are emitted as `health.diagnostics` realtime events for local visibility.

## Configuration Surface

Current `.env.example` keys include:

- `DEEPGRAM_KEY`
- `ANTHROPIC_KEY`
- `WHISPER_API_KEY`
- `TRANSLATION_API_KEY`
- `LOCAL_AGENT_WS_HOST`
- `LOCAL_AGENT_WS_PORT`
- `DEFAULT_LANGUAGE`
- `ZERO_STORAGE_MODE`
- `AUDIO_DEVICE_NAME`
- `AUDIO_SAMPLE_RATE`
- `AUDIO_CHUNK_MS`
- `ASR_PRIMARY_PROVIDER`
- `ASR_FALLBACK_ENABLED`
- `ASR_PRIMARY_TIMEOUT_MS`
- `LANGUAGE_DETECTION_ENABLED`
- `TRANSLATION_ENABLED`
- `INTENT_LLM_ASSIST_ENABLED`
- `ANSWER_MAX_TOKENS`
- `ANSWER_PROVIDER_TIMEOUT_MS`

## Security Baseline

- Keep API keys local to agent runtime.
- Do not expose provider keys to browser runtime.
- Keep zero-storage mode enabled by default unless explicitly changed.
- Keep localhost-only binding unless a later phase intentionally introduces remote exposure controls.

## Packaging / Validation State

Phase 07 validated:

- Python tests PASS
- Web tests PASS
- Web build PASS
- Local baseline transcript-to-answer latency measurement median: `0.020 ms`

Measurement note: the recorded latency reflects the implemented local in-process routing path available in this repo, not an external provider round-trip.
