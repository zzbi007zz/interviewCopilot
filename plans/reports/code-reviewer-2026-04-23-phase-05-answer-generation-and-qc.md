## Code Review Summary

### Scope
- Files: `/Users/february10/Documents/interviewCopilot/agent/answer_client.py`, `/Users/february10/Documents/interviewCopilot/agent/qc_prompt_template.py`, `/Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py`, `/Users/february10/Documents/interviewCopilot/agent/answer_fallback.py`, `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py`, `/Users/february10/Documents/interviewCopilot/agent/message_router.py`, `/Users/february10/Documents/interviewCopilot/agent/config.py`, `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts`, `/Users/february10/Documents/interviewCopilot/.env.example`, `/Users/february10/Documents/interviewCopilot/shared/config-contracts.md`
- LOC: 890
- Focus: Phase 05 pre-landing gate
- Scout findings: downstream dependents are websocket consumers of `answer.generated`; edge cases are duplicate finals, provider timeout/failure fallback, language normalization at contract boundary, and malformed model output that still superficially resembles Option A/B.

### Overall Assessment
FAIL. The phase is close, but two production-significant issues remain: the emitted `answer.generated.language` can disagree with the actual answer language, and the parser accepts extra prose inside answer sections instead of enforcing the deterministic contract the phase depends on. Error redaction posture for provider failures is otherwise good: provider exceptions are swallowed into fallback behavior and not surfaced to websocket clients.

### Critical Issues
- None.

### High Priority
1. Contract mismatch: `answer.generated.language` can emit unsupported/incorrect values such as `auto` while the provider is instructed to answer in English.
   - File: `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py:50`
   - Supporting lines: `/Users/february10/Documents/interviewCopilot/agent/qc_prompt_template.py:4-5`, `/Users/february10/Documents/interviewCopilot/agent/answer_fallback.py:88-95`
   - Why it matters: when language detection is disabled or `DEFAULT_LANGUAGE=auto`, success path returns `pipeline.language` verbatim, but prompt generation collapses every non-`vi` value to English. UI and downstream logic will believe the payload language is `auto` even though content is English. Fallback path normalizes to `en`, so success and fallback paths disagree on the same input.
   - Impact: silent contract drift that can break Phase 06 rendering assumptions and analytics keyed on `en|vi`.
   - Evidence snippet:
     ```py
     # /Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py:45-53
     return AnswerPayload(
         source_text=source_text,
         question_type=pipeline.question_type,
         option_a=parsed.option_a,
         option_b=parsed.option_b,
         language=pipeline.language,
         fallback_used=False,
         qc_status="passed",
     )
     ```
     ```py
     # /Users/february10/Documents/interviewCopilot/agent/qc_prompt_template.py:4-5
     def _target_language(language: str) -> str:
         return "Vietnamese" if language.strip().lower() == "vi" else "English"
     ```

### Medium Priority
1. Output parser is too permissive and accepts arbitrary prose inside Option sections, including text that is not a bullet.
   - File: `/Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py:30-52`
   - Why it matters: phase plan and QC design rely on deterministic `Option A`/`Option B` bullet-only output. Current parser treats any non-empty line as a bullet after minimal normalization, so malformed provider output can pass as `qc_status="passed"` instead of degrading to fallback.
   - Production risk: format drift reaches UI without triggering fallback. This is exactly the kind of latent model-behavior bug that passes happy-path testing and breaks in production.
   - Repro used during review:
     ```py
     sample = '''Option A:
Here is a concise answer:
- first
- second
Option B:
- third
- fourth
'''
     parse_answer_output(sample)
     # ParsedAnswer(option_a=['Here is a concise answer:', 'first', 'second'], option_b=['third', 'fourth'])
     ```
   - Evidence snippet:
     ```py
     # /Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py:32-47
     for raw_line in block.splitlines():
         line = raw_line.strip()
         if not line:
             continue

         normalized = line
         if line.startswith("- "):
             normalized = line[2:]
         elif line.startswith("*"):
             normalized = line[1:].strip()
         elif line[:2].isdigit() and "." in line:
             normalized = line.split(".", 1)[1].strip()

         normalized = " ".join(normalized.split())
         if normalized:
             bullets.append(normalized)
     ```

### Low Priority
1. No Phase 05 automated tests were found for parser/orchestrator/config/contract behavior.
   - Evidence: repository search found no matching test files covering `answer_output_parser`, `answer_orchestrator`, `qc_prompt_template`, or the new answer event contract.
   - Why it matters: the two issues above are both regressions that targeted unit/integration tests should catch.
2. `agent/message_router.py:11-16` defines `_safe_error_message`, but current ASR error path always passes the constant string `"ASR provider failure"` at `/Users/february10/Documents/interviewCopilot/agent/message_router.py:79`, so the sanitizer is effectively unexercised for dynamic text.

### Edge Cases Found by Scout
- Duplicate final transcript path is protected before answer generation at `/Users/february10/Documents/interviewCopilot/agent/message_router.py:35-39`; good.
- Provider timeout / SDK unavailable / missing key all degrade to fallback in `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py:42-64`; good redaction posture because no raw provider exception text is emitted.
- Boundary-condition risk: `DEFAULT_LANGUAGE=auto` or disabled language detection causes contract ambiguity for `answer.generated.language`.
- Boundary-condition risk: malformed model output with extra prose is currently accepted as success instead of triggering fallback.

### Positive Observations
- `/Users/february10/Documents/interviewCopilot/agent/answer_client.py:52-64` correctly maps timeout and generic provider failures to redacted internal error codes rather than leaking exception strings.
- `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts:133-139` and `:196-201` reject leaked secrets/stack traces in `error` events.
- `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts:52-63` keeps `answer.generated` additive and backward-compatible with prior `optionA/optionB/language` shape.
- Python syntax validation passed for all reviewed Phase 05 agent files.

### Recommended Actions
1. Normalize answer language once at the orchestrator boundary and emit only supported concrete values (`en` or `vi`) on both success and fallback paths.
2. Tighten `/Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py` so only explicit bullet lines are accepted; any extra prose should fail parsing and force fallback.
3. Add unit tests for parser strictness, language normalization, fallback on provider errors, and shared contract validation for `answer.generated`.
4. Optional: if product wants visibility into degraded mode, emit one redacted `error` event alongside fallback with a generic message only.

### Metrics
- Type Coverage: not measured in this review
- Test Coverage: no Phase 05 automated coverage found for new answer-generation modules/contracts
- Linting Issues: 0 syntax issues in reviewed Python files (`py_compile` passed)

### Unresolved Questions
- Should `answer.generated.language` contract be constrained to `en | vi` now, or is a broader language enum intentionally planned for later phases?
- On fallback, should the agent emit only `answer.generated` or also a redacted `error` event for UI observability?

### Gate Verdict
FAIL
