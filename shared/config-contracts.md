# Config Contracts (v1.0.0)

This file defines runtime configuration contracts shared across local agent and web client integration boundaries.

## Principles

- Secrets stay in local agent environment only.
- Web runtime must never require provider secrets.
- Additive changes only for v1.x compatibility.

## Environment Variables

| Variable | Required | Default | Scope | Notes |
|---|---|---|---|---|
| `DEEPGRAM_KEY` | no | empty | agent | Cloud ASR provider key |
| `ANTHROPIC_KEY` | no | empty | agent | Answer generation provider key |
| `WHISPER_API_KEY` | no | empty | agent | Optional ASR fallback key |
| `TRANSLATION_API_KEY` | no | empty | agent | Optional translation provider key |
| `LOCAL_AGENT_WS_HOST` | no | `127.0.0.1` | agent/web bridge | Local websocket host |
| `LOCAL_AGENT_WS_PORT` | no | `8765` | agent/web bridge | Local websocket port (1-65535) |
| `DEFAULT_LANGUAGE` | no | `auto` | agent | Language hint for pipeline |
| `ZERO_STORAGE_MODE` | no | `true` | agent | Enables non-persistent mode |
| `AUDIO_DEVICE_NAME` | no | `BlackHole` | agent | Preferred local audio loopback device label |
| `AUDIO_SAMPLE_RATE` | no | `16000` | agent | Audio sample rate for capture pipeline |
| `AUDIO_CHUNK_MS` | no | `250` | agent | Target audio chunk cadence in milliseconds |
| `ASR_PRIMARY_PROVIDER` | no | `deepgram` | agent | Primary ASR provider selector for phase-04 baseline |
| `ASR_FALLBACK_ENABLED` | no | `true` | agent | Enables one-way fallback to local ASR path |
| `ASR_PRIMARY_TIMEOUT_MS` | no | `3000` | agent | Timeout threshold for primary ASR before fallback |
| `LANGUAGE_DETECTION_ENABLED` | no | `true` | agent | Enables transcript language detection pipeline |
| `TRANSLATION_ENABLED` | no | `false` | agent | Enables optional translation layer (no-op in phase-04 baseline) |
| `INTENT_LLM_ASSIST_ENABLED` | no | `false` | agent | Enables optional LLM intent assist fallback |
| `ANSWER_MAX_TOKENS` | no | `200` | agent | Max output tokens for answer generation provider |
| `ANSWER_PROVIDER_TIMEOUT_MS` | no | `2500` | agent | Timeout threshold for answer generation provider |

## Validation Rules

1. `LOCAL_AGENT_WS_PORT` must be integer and in range `1..65535`.
2. `LOCAL_AGENT_WS_HOST` must be non-empty and local-only (`127.0.0.1` or `localhost`) by default.
3. `DEFAULT_LANGUAGE` must be non-empty.
4. `ZERO_STORAGE_MODE` accepts `1|true|yes|on` as true and `0|false|no|off` as false (case-insensitive). Any other value must fail startup validation.
5. `AUDIO_SAMPLE_RATE` must be integer and greater than 0.
6. `AUDIO_CHUNK_MS` must be integer and greater than 0.
7. `AUDIO_DEVICE_NAME` should be non-empty for deterministic audio probe behavior.
8. `ASR_PRIMARY_PROVIDER` must be `deepgram` for phase-04 baseline.
9. `ASR_PRIMARY_TIMEOUT_MS` must be integer and greater than 0.
10. `ASR_FALLBACK_ENABLED`, `LANGUAGE_DETECTION_ENABLED`, `TRANSLATION_ENABLED`, and `INTENT_LLM_ASSIST_ENABLED` use strict bool parsing (`1|true|yes|on|0|false|no|off`).
11. `ANSWER_MAX_TOKENS` must be integer and greater than 0.
12. `ANSWER_PROVIDER_TIMEOUT_MS` must be integer and greater than 0.

## Runtime Exposure Rules

- Agent can read all variables above.
- Web must read only non-secret connection settings derived from agent handshake/config endpoint.
- Errors must redact provider keys and stack internals.

## Versioning Policy

- Contract version: `1.0.0`
- v1 changes must remain backward-compatible and additive.
- Breaking contract changes require major version bump.
