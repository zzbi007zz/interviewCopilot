# Phase 03 — Build local agent foundation (audio + websocket)

## Context Links
- Plan overview: `./plan.md`
- Depends on: `phase-02-define-shared-realtime-protocol-and-config-contracts.md`

## Overview
- Priority: Critical
- Status: Completed
- Purpose: Build Python local service to capture audio and stream protocol events to UI.

## Key Insights
- Audio capture and low-latency chunking are the backbone.
- Service must tolerate device-change and stream interruption gracefully.

## Requirements
- Functional:
  1. Build local websocket server for browser UI clients.
  2. Implement audio capture abstraction (BlackHole/system loopback first).
  3. Emit health/status and transcript-stream placeholder events.
- Non-functional:
  1. Chunk cadence around 250ms.
  2. Robust startup diagnostics for missing audio device.

## Architecture
- Modules:
  - `agent/main.py`: bootstrap + lifecycle
  - `agent/audio-capture.py`: capture abstraction
  - `agent/ws-hub.py`: client sessions + broadcast
  - `agent/runtime-state.py`: transient in-memory state

## Related Code Files
- `agent/main.py`
- `agent/audio-capture.py`
- `agent/ws-hub.py`
- `agent/config.py`
- `agent/requirements.txt`

## Implementation Steps
1. Build app startup and config validation.
2. Add websocket server and connection manager.
3. Add capture provider interface and BlackHole implementation.
4. Publish status events and audio chunk pipeline hooks.

## Todo List
- [x] Implement startup and env validation
- [x] Implement websocket hub and broadcast model
- [x] Implement capture provider interface
- [x] Emit lifecycle events for UI observability

## Success Criteria
- Local agent runs and accepts websocket clients.
- Agent captures audio frames and exposes stream hooks.

## Risk Assessment
- Risk: BlackHole device discovery varies by machine.
- Mitigation: dynamic discovery + explicit config override.

## Security Considerations
- Bind server to localhost by default.
- Reject non-local origins unless explicitly allowed.

## Next Steps
- Connect stream to ASR and NLP pipeline in Phase 04.
