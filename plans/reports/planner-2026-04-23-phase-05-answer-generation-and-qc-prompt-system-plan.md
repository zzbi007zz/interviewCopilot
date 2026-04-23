# Phase 05 implementation plan — answer generation and QC prompt system

## Scope lock
Implement minimal answer generation after Phase 04 final transcript + intent output. No speculative memory, no streaming token UI, no multi-provider routing beyond one Anthropic client + one deterministic fallback.

## Current state summary
- `agent/message_router.py` already emits `transcript.final` and `intent.detected` after `process_final_transcript(...)`.
- `agent/language_and_intent_pipeline.py` already returns normalized text, language, question type, keywords.
- `shared/realtime-event-contracts.ts` already defines `answer.generated`, but payload too thin for safe fallback/QC state.
- `web/src/lib/protocol.ts` already re-exports shared protocol parsing; no extra parser layer needed if shared contract updated.
- `agent/config.py` already exposes `anthropic_key`; no answer-generation-specific config yet.

## Minimal implementation plan

### 1. Keep data flow linear
Input:
- final ASR transcript
- detected language
- detected question type
- extracted keywords

Transform:
- build deterministic QC prompt from transcript + pipeline output
- call Anthropic client with bounded tokens
- parse strict Option A / Option B sections
- normalize to UI-safe payload
- fallback to deterministic local answer when provider fails or output invalid

Output:
- `answer.generated` event to websocket clients
- optional `error` event only for internal-visible pipeline state, but redacted

### 2. Files to create
1. `/Users/february10/Documents/interviewCopilot/agent/answer_client.py`
   - Anthropic wrapper only
   - one method: generate_answer(prompt, language)
   - enforce timeout / max tokens / redacted exception mapping
2. `/Users/february10/Documents/interviewCopilot/agent/qc_prompt_template.py`
   - deterministic prompt builder
   - one function returns system/user prompt text from transcript + question type + keywords + language
3. `/Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py`
   - parse model text into Option A / Option B bullet arrays
   - reject malformed output, trim bullet count, trim line length
4. `/Users/february10/Documents/interviewCopilot/agent/answer_fallback.py`
   - deterministic fallback answers by language
   - no provider dependency
5. `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py`
   - orchestrates prompt build -> provider call -> parse -> fallback -> return normalized payload

### 3. Files to modify
1. `/Users/february10/Documents/interviewCopilot/agent/message_router.py`
   - after `intent.detected`, call answer orchestrator on final transcript path
   - emit `answer.generated`
   - keep `partial` path unchanged
2. `/Users/february10/Documents/interviewCopilot/agent/config.py`
   - add minimal answer config:
     - `answer_max_tokens: int`
     - `answer_provider_timeout_ms: int`
   - validate positive ints
   - do not add provider switching yet
3. `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts`
   - expand `AnswerGeneratedEvent` payload schema
   - validate fallback/error-safe metadata fields
4. `/Users/february10/Documents/interviewCopilot/web/src/lib/protocol.ts`
   - no shape logic change if parser remains shared-only
   - modify only if TS exports need updated event payload typing surfaced explicitly

## Exact event contract payload shape
Add in `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts` under `AnswerGeneratedEvent`:

```ts
export type AnswerGeneratedEvent = BaseEvent & {
  type: typeof EVENT_TYPES.ANSWER_GENERATED
  payload: {
    sourceText: string
    language: string
    questionType: string
    optionA: string[]
    optionB: string[]
    fallbackUsed: boolean
    qcStatus: 'passed' | 'fallback'
  }
}
```

Why this shape:
- `sourceText`: lets UI correlate answer with transcript without extra lookup
- `language`: keeps Phase 06 rendering deterministic
- `questionType`: avoids recomputation in UI
- `optionA` / `optionB`: matches current event concept
- `fallbackUsed`: observable, testable, avoids hidden degraded mode
- `qcStatus`: explicit success/fallback state without leaking provider internals

Do not add raw provider name, latency, prompt, or error details to UI event in this phase.

## Safe fallback behavior
On any provider failure, timeout, missing key, parse failure, or empty output:
1. Do not raise raw exception to UI.
2. Emit `answer.generated` with deterministic fallback payload.
3. Set:
   - `fallbackUsed: true`
   - `qcStatus: 'fallback'`
4. Optionally emit redacted `error` event:
   - code: `ANSWER_GENERATION_FAILED`
   - message: `Answer generation unavailable. Using fallback response.`
   - retryable: true

Fallback content rules:
- language follows pipeline language, else config default
- exactly 2-3 bullets per option
- generic but interview-safe
- no fabricated company-specific facts
- no raw provider diagnostics, tracebacks, auth hints, or key markers

Example fallback payload:

```json
{
  "sourceText": "How do you handle flaky UI tests?",
  "language": "en",
  "questionType": "qa-automation",
  "optionA": [
    "I first isolate whether the flake comes from test timing, unstable selectors, or test data.",
    "Then I stabilize waits and selectors before deciding if the test should be rewritten or quarantined."
  ],
  "optionB": [
    "I review failures by pattern, not one run in isolation.",
    "My goal is to remove root causes like race conditions, environment drift, and brittle assertions."
  ],
  "fallbackUsed": true,
  "qcStatus": "fallback"
}
```

## Minimal implementation steps
1. Create `qc_prompt_template.py`
   - fixed template
   - inputs: transcript, language, question_type, keywords
   - outputs instruction to return only:
     - `Option A:` bullets
     - `Option B:` bullets
   - hard bound tone: concise, interview-ready, no markdown tables, no prose intro
2. Create `answer_client.py`
   - minimal Anthropic call wrapper using `anthropic_key`
   - enforce timeout and max tokens
   - return plain text only
3. Create `answer_output_parser.py`
   - parse two sections only
   - strip numbering/bullets to normalized string arrays
   - reject if either option missing or empty
4. Create `answer_fallback.py`
   - deterministic EN/VI fallback templates keyed by `question_type`, default generic unknown
5. Create `answer_orchestrator.py`
   - input: transcript text + `PipelineOutput` + config
   - branch:
     - no anthropic key => fallback
     - provider fail => fallback
     - parse fail => fallback
     - success => qc passed payload
6. Modify `message_router.py`
   - call orchestrator immediately after `intent.detected`
   - set runtime status to `responding` before call if state model reused, then back to `processing` or leave unchanged if minimizing scope
   - emit one `answer.generated` event per final transcript
7. Modify `shared/realtime-event-contracts.ts`
   - add new fields to validator and exported TS type
8. Modify `web/src/lib/protocol.ts` only if shared type export causes compile nits

## Dependency graph
- Phase 04 output in `language_and_intent_pipeline.py` blocks Phase 05 orchestrator input
- `config.py` update blocks `answer_client.py` timeout/max-token config
- shared contract update blocks any Phase 06 UI consumption
- `message_router.py` integration depends on orchestrator module complete

## File ownership / parallel safety
- Backend Phase 05 work owns only:
  - `/Users/february10/Documents/interviewCopilot/agent/*.py` listed above
  - `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts`
- Frontend Phase 06 should not edit `agent/*`
- If protocol export tweak needed in `/Users/february10/Documents/interviewCopilot/web/src/lib/protocol.ts`, do it last to avoid overlap

## Risks and mitigations
1. Risk: model output format drift
   - Likelihood: High
   - Impact: High
   - Mitigation: strict parser + deterministic fallback, prompt asks for exact headings only
2. Risk: response latency hurts live use
   - Likelihood: Medium
   - Impact: High
   - Mitigation: bound max tokens, no multi-turn context, no retries in Phase 05
3. Risk: provider error leaks secrets or stack traces
   - Likelihood: Medium
   - Impact: High
   - Mitigation: central redaction in `answer_client.py`, UI sees generic message only
4. Risk: duplicate final transcript triggers duplicate answers
   - Likelihood: Medium
   - Impact: Medium
   - Mitigation: rely on existing transcript dedupe before orchestrator call; no extra dedupe layer needed now
5. Risk: shared contract change breaks web parsing
   - Likelihood: Low
   - Impact: Medium
   - Mitigation: keep additive fields, preserve `optionA`, `optionB`, `language`

## Backwards compatibility
- Keep existing `answer.generated` event name unchanged.
- Preserve current fields: `optionA`, `optionB`, `language`.
- Only add additive fields; Phase 06 consumers can ignore extras.
- If any consumer still expects old shape, contract remains valid because required old fields stay intact.

## Rollback plan
1. Revert `message_router.py` answer orchestrator call.
2. Revert shared contract additive fields if UI breaks.
3. Leave ASR + intent pipeline intact.
4. Since no persisted data/migration exists, rollback is code-only and isolated.

## Test matrix
### Unit
- `qc_prompt_template.py`
  - EN prompt contains transcript/question type/keywords
  - VI prompt enforces VI answer language
- `answer_output_parser.py`
  - valid Option A/B parse
  - malformed output rejected
  - extra prose stripped/rejected
- `answer_fallback.py`
  - EN and VI fallback shapes stable
  - unknown question type still returns safe generic output
- `config.py`
  - timeout/max-token env parsing and validation

### Integration
- `message_router.py`
  - final transcript emits `transcript.final`, `intent.detected`, `answer.generated`
  - provider fail path still emits `answer.generated` fallback
  - duplicate final transcript emits nothing extra
- `shared/realtime-event-contracts.ts`
  - valid answer event passes
  - invalid answer event rejected when fields wrong

### E2E-lite / gate verification
- run agent with no Anthropic key -> fallback answer event visible, no crash
- run agent with mocked/sandboxed provider success -> answer event with `fallbackUsed: false`
- verify web protocol parser accepts envelope containing `answer.generated`
- verify error event message contains no secret markers/traceback text

## Review checklist for Phase 05 gate
- [ ] One final transcript produces exactly one `answer.generated` event
- [ ] Event payload matches shared contract exactly
- [ ] EN input returns EN answer; VI input returns VI answer
- [ ] Missing key / timeout / parse failure all degrade to safe fallback
- [ ] No raw provider error text reaches websocket payloads
- [ ] Existing transcript and intent events still emitted unchanged
- [ ] New Python files use underscore naming and stay near or under 200 LOC each
- [ ] Shared contract remains additive; no breaking rename of existing fields
- [ ] Unit + integration tests added and passing
- [ ] QA report explicitly marks PASS before tracker doc update

## Success criteria
- Observable: websocket emits `answer.generated` after final transcript in both success and fallback paths
- Observable: payload contains two answer options, language, question type, fallback state
- Observable: provider failures do not crash agent startup or final transcript processing
- Observable: TS protocol validator accepts new payload shape

## Unresolved questions
- Exact Anthropic SDK usage already present anywhere in repo, or Phase 05 should add first provider client from scratch?
- Should fallback also emit `error` event, or only `answer.generated` with `fallbackUsed: true` to reduce UI noise?
