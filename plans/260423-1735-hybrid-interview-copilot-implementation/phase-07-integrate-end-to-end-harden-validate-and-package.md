# Phase 07 — Integrate end-to-end, harden, validate, and package

## Context Links
- Plan overview: `./plan.md`
- Depends on: phases 03, 04, 05, 06

## Overview
- Priority: Critical
- Status: Completed
- Purpose: Validate full pipeline behavior, harden failures, and prepare practical local usage.

## Key Insights
- E2E reliability matters more than adding extra features.
- Must verify latency target with realistic meeting audio.

## Requirements
- Functional:
  1. Wire full path: audio -> ASR -> intent -> answer -> UI.
  2. Add health checks and diagnostics endpoints/events.
  3. Package startup scripts and env templates.
- Non-functional:
  1. Validate latency target (`<=1.5s` median in expected environment).
  2. Add baseline tests for protocol and core pipeline behavior.

## Architecture
- Integration tests validate boundaries:
  - ASR adapter contract
  - Answer generation output format
  - websocket broadcast flow

## Related Code Files
- `tests/` (agent + web integration tests)
- `scripts/start-local-dev.sh`
- `scripts/check-system-audio-prereqs.sh`
- `README.md`
- `docs/deployment-guide.md`
- `docs/system-architecture.md`
- `docs/project-roadmap.md`

## Implementation Steps
1. Add integration test suite and run baseline.
2. Add runtime health/status diagnostics.
3. Add packaging/start scripts and setup instructions.
4. Perform latency test run and record results.
5. Update docs and changelog artifacts.

## Todo List
- [x] Implement E2E integration checks
- [x] Add health diagnostics and error taxonomy
- [x] Add setup/start scripts
- [x] Measure and document latency results
- [x] Update docs and roadmap/changelog

## Success Criteria
- Full demo run works from local audio to overlay answer display.
- Core tests pass consistently.
- Setup path is documented and reproducible.
- Health diagnostics and explicit error taxonomy are emitted through the shared runtime contract.
- Local baseline transcript-to-answer latency is measured and recorded with method + median evidence.

## Risk Assessment
- Risk: Environment-specific audio setup failures.
- Mitigation: preflight script and explicit troubleshooting matrix.

## Security Considerations
- Reconfirm no secret leakage to client logs.
- Keep localhost-only defaults and explicit opt-in for remote exposure.

## Next Steps
- Phase closed after QA PASS and tracking sync.
- Ready for user-directed follow-up work or live environment validation.
