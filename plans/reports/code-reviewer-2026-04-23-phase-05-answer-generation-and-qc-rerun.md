## Code Review Summary

### Scope
- Files: `/Users/february10/Documents/interviewCopilot/agent/answer_client.py`, `/Users/february10/Documents/interviewCopilot/agent/qc_prompt_template.py`, `/Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py`, `/Users/february10/Documents/interviewCopilot/agent/answer_fallback.py`, `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py`, `/Users/february10/Documents/interviewCopilot/agent/message_router.py`, `/Users/february10/Documents/interviewCopilot/agent/config.py`, `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts`, `/Users/february10/Documents/interviewCopilot/tests/test_phase_05_answer_modules.py`, `/Users/february10/Documents/interviewCopilot/.env.example`, `/Users/february10/Documents/interviewCopilot/shared/config-contracts.md`
- LOC: ~700 reviewed in scoped files
- Focus: Phase 05 rerun after fixes
- Scout findings: downstream dependents remain websocket consumers of `answer.generated`; key edge cases are `DEFAULT_LANGUAGE=auto`, disabled language detection, malformed provider output containing extra prose plus valid bullets, provider timeout/sdk absence, and contract drift between Python emitter and TS validator.

### Overall Assessment
FAIL. One prior blocker is fixed: `answer.generated.language` now normalizes consistently at the orchestrator boundary and matches fallback behavior. Provider-failure redaction posture is still good. But parser strictness is still not fully fixed: extra non-bullet prose inside an option block is silently ignored instead of rejected, so malformed model output can still pass QC and reach production clients. There is also a remaining contract looseness where the shared TS contract still allows any answer language string even though runtime behavior is now effectively `en | vi`.

### Critical Issues
- None.

### High Priority
1. Parser still accepts malformed option blocks when extra prose is present alongside enough valid bullets.
   - File: `/Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py:30-52`
   - Why it matters: the phase contract requires deterministic bullet-only `Option A` / `Option B` output. Current logic ignores non-bullet lines instead of failing the parse. In production, LLM drift such as preambles or explanatory sentences can still produce `qc_status="passed"` and leak off-contract content patterns through the success path.
   - Concrete repro:
     ```py
     sample = '''Option A:
     Intro sentence that should fail QC
     - first
     - second
     Option B:
     - third
     - fourth
     '''
     parse_answer_output(sample)
     # currently passes, because the prose line is ignored
     ```
   - Evidence snippet:
     ```py
     # /Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py:32-47
     for raw_line in block.splitlines():
         line = raw_line.strip()
         if not line:
             continue

         normalized = ""
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
   - Fix direction: reject any non-empty line that is not an allowed bullet marker, rather than skipping it.

### High Priority
2. Contract consistency is still weaker than runtime guarantee for `answer.generated.language`.
   - File: `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts:54-62,177-189`
   - Why it matters: Python now emits normalized concrete values (`en` or `vi`) via `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py:24-25,33-39,50-57`, but the shared contract still validates any string. That means downstream consumers cannot rely on the stronger guarantee, and a future regression could reintroduce `auto` without TypeScript contract checks catching it.
   - Evidence snippet:
     ```ts
     // /Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts:59
     language: string
     ```
   - Fix direction: tighten the TS event contract and validator to `en | vi` if Phase 05 intends that as the stable interface.

### Medium Priority
1. Test coverage improved but still misses the real parser-regression shape.
   - File: `/Users/february10/Documents/interviewCopilot/tests/test_phase_05_answer_modules.py:38-47`
   - Why it matters: the added test only covers prose replacing a bullet, which fails because Option A drops below the 2-bullet minimum. It does not cover the more dangerous case where prose is present and both required bullets still exist, which is the path that currently slips through.
   - Evidence snippet:
     ```py
     malformed = """Option A:
     This line should be rejected
     - Bullet one
     Option B:
     - Bullet two
     - Bullet three
     """
     ```

### Low Priority
1. `_safe_error_message` remains effectively unexercised for dynamic text in ASR routing.
   - File: `/Users/february10/Documents/interviewCopilot/agent/message_router.py:11-16,74-81`
   - Current code always passes the constant string `"ASR provider failure"`, so sanitizer behavior is good in posture but not validated in live code path.

### Edge Cases Found by Scout
- Duplicate final transcript suppression remains in place at `/Users/february10/Documents/interviewCopilot/agent/message_router.py:35-39`.
- Provider timeout / missing key / SDK absence still degrade to fallback without leaking raw exception text because `/Users/february10/Documents/interviewCopilot/agent/answer_client.py:61-68` maps failures to redacted internal error codes and `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py:59-69` swallows them into fallback payloads.
- `DEFAULT_LANGUAGE=auto` no longer leaks through `answer.generated.language`; success and fallback now converge on `en` for non-`vi` values via `/Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py:24-25,33,55` and `/Users/february10/Documents/interviewCopilot/agent/answer_fallback.py:87-95`.
- Malformed model output with mixed prose plus bullets still passes parser QC today.
- Shared contract does not yet enforce the normalized language domain that runtime now provides.

### Positive Observations
- Language normalization bug called out in prior review is fixed. Evidence:
  ```py
  # /Users/february10/Documents/interviewCopilot/agent/answer_orchestrator.py:24-25
  def _normalize_language_code(language: str) -> str:
      return "vi" if language.strip().lower() == "vi" else "en"
  ```
- Provider failure redaction posture remains sound in `/Users/february10/Documents/interviewCopilot/agent/answer_client.py:42-68`; no raw provider exception text is emitted to clients.
- Shared `error` event validator still rejects secrets and stack traces in `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts:99-100,133-139,196-201`.
- Scoped tests pass and reviewed Python files compile successfully.

### Recommended Actions
1. Make `/Users/february10/Documents/interviewCopilot/agent/answer_output_parser.py` fail fast on any non-empty non-bullet line inside option blocks.
2. Add a regression test covering prose plus two valid bullets in the same option block.
3. Tighten `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts` so `answer.generated.language` matches runtime guarantee (`en | vi`) if that is the intended Phase 05 contract.
4. Optional: add one contract test that validates a bad `answer.generated.language` such as `auto` is rejected.

### Metrics
- Type Coverage: not measured in this review
- Test Coverage: targeted Phase 05 tests present, but parser edge-case coverage incomplete
- Linting Issues: 0 syntax issues in reviewed Python files (`python3 -m py_compile` passed)
- Test Result: PASS for `/Users/february10/Documents/interviewCopilot/tests/test_phase_05_answer_modules.py`

### Unresolved Questions
- Is `answer.generated.language` now officially constrained to `en | vi`, or do later phases intentionally need a wider enum?
- Should parser allow numbered bullets and `*` bullets long term, or should the runtime contract be tightened to only `- ` for maximum determinism?

### Gate Verdict
FAIL
