# Phase 02 — Define shared realtime protocol and config contracts

## Context Links
- Plan overview: `./plan.md`
- Depends on: `phase-01-bootstrap-repository-and-architecture-docs.md`

## Overview
- Priority: Critical
- Status: Completed
- Purpose: Define websocket event model and configuration contracts used by both local agent and web client.

## Key Insights
- Integration failures usually come from schema drift.
- A single source of truth for events keeps agent/web decoupled but compatible.

## Requirements
- Functional:
  1. Define event types for transcript partial/final, intent, answer, status, and error.
  2. Define payload schemas and validation strategy.
  3. Define env var contracts and defaults.
- Non-functional:
  1. Version the protocol.
  2. Backward-compatible additive changes only after v1.

## Architecture
- `shared/protocol` module stores:
  - `protocol-version`
  - event names
  - payload type definitions
  - runtime validators (lightweight)

## Related Code Files
- `shared/realtime-event-contracts.ts` (or `.py` equivalents)
- `shared/config-contracts.md`
- `agent/config.py`
- `web/src/lib/protocol.ts`

## Implementation Steps
1. Draft protocol spec from brief pipeline.
2. Define each event payload schema with examples.
3. Implement lightweight validation in agent and web adapter.
4. Add protocol conformance test fixtures.

## Todo List
- [x] Define event taxonomy and naming
- [x] Create payload schema definitions
- [x] Implement shared validation hooks
- [x] Add sample fixtures and contract checks

## Success Criteria
- Agent and UI can deserialize/serialize same events without custom mapping hacks.
- Config variables documented and validated at startup.

## Risk Assessment
- Risk: Schema too rigid for interim transcripts.
- Mitigation: keep required fields minimal; allow additive metadata map.

## Security Considerations
- Never include secrets in event payloads.
- Error payloads must redact provider keys and raw stack traces.

## Next Steps
- Proceed to local agent foundation with protocol frozen at v1.
