# Phase 05 — Implement answer generation and QC prompt system

## Context Links
- Plan overview: `./plan.md`
- Depends on: `phase-04-implement-asr-language-intent-pipeline.md`

## Overview
- Priority: High
- Status: Completed
- Purpose: Generate concise interview-ready responses using fixed QC prompt templates.

## Key Insights
- Stable response formatting improves readability and trust in live interviews.
- Prompt construction should be deterministic and auditable.

## Requirements
- Functional:
  1. Implement LLM client abstraction (Anthropic primary).
  2. Implement QC prompt template from brief6.
  3. Support EN/VI output match to detected input language.
  4. Emit Option A / Option B structured answer events.
- Non-functional:
  1. Keep max tokens bounded.
  2. Add safe fallback response on model failures.

## Architecture
- `agent/answer-client.py`
- `agent/qc-prompt-template.py`
- `agent/answer-orchestrator.py`

## Related Code Files
- `agent/answer-client.py`
- `agent/qc-prompt-template.py`
- `agent/answer-orchestrator.py`
- `agent/message-router.py`

## Implementation Steps
1. Implement provider wrapper for Claude calls.
2. Encode prompt template and output parser.
3. Add language-conditioned output logic.
4. Broadcast structured answer events to UI.

## Todo List
- [x] Add LLM provider wrapper
- [x] Implement prompt builder
- [x] Add output parsing and normalization
- [x] Emit answer events and fallback responses

## Success Criteria
- Final transcript produces two concise formatted answer options.
- Output language follows detected/selected language.

## Risk Assessment
- Risk: Overlong responses or format drift.
- Mitigation: explicit output parser + truncation guard.

## Security Considerations
- Never expose API key or raw provider diagnostics to UI.

## Next Steps
- Integrate with web overlay rendering in Phase 06.
