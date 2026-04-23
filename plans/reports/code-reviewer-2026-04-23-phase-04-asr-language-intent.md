## Code Review Summary

### Scope
- Files: `/Users/february10/Documents/interviewCopilot/agent/asr_provider.py`, `/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py`, `/Users/february10/Documents/interviewCopilot/agent/asr_local_fallback.py`, `/Users/february10/Documents/interviewCopilot/agent/language_and_intent_pipeline.py`, `/Users/february10/Documents/interviewCopilot/agent/message_router.py`, `/Users/february10/Documents/interviewCopilot/agent/main.py`, `/Users/february10/Documents/interviewCopilot/agent/config.py`
- Focus: requested Phase 04 ASR/language/intent review
- Scout findings: `git diff --name-only HEAD~1` did not return `interviewCopilot` paths, so review was scoped to requested files plus affected dependents `/Users/february10/Documents/interviewCopilot/agent/runtime_state.py`, `/Users/february10/Documents/interviewCopilot/agent/ws_hub.py`, `/Users/february10/Documents/interviewCopilot/agent/audio_capture.py`, and shared contracts.

### Overall Assessment
Phase 04 is not production-ready. The current baseline compiles, but realtime ordering, timeout semantics, and duplicate suppression behavior can silently drop or mis-sequence user-visible events under normal runtime conditions. Config validation mostly matches the contract, but a few behavior/message mismatches remain.

### Critical Issues
1. **Session-age timeout makes primary ASR fail permanently after timeout window**  
   - File: `/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py:27-35`  
   - Problem: timeout is computed from provider start time, not from request/chunk activity. After `timeout_ms` elapses once, every later `push_audio()` emits `ASR_PRIMARY_TIMEOUT`, even if the provider was healthy moments earlier.  
   - Impact: long interview sessions will deterministically degrade into fallback/error mode after ~3s default runtime. This passes smoke tests but breaks production sessions.  
   - Fix: track per-request/per-stream inactivity or provider response timeout, and reset timeout state on successful transcript activity.

2. **ASR callback handling introduces async race conditions and unhandled task failures**  
   - File: `/Users/february10/Documents/interviewCopilot/agent/main.py:45-62`  
   - Problem: provider callbacks schedule `asyncio.create_task(handle_asr_result(item))` for each result with no ordering control and no task exception handling. Providers emit partial/final synchronously, so routing can race; exceptions inside `route_asr_result()` become unobserved task failures.  
   - Impact: partial/final ordering can become nondeterministic, fallback switching can race on repeated errors, and broadcast/pipeline exceptions can be lost outside the main error boundary.  
   - Fix: serialize ASR result processing through an `asyncio.Queue` or a single consumer task, and wrap task execution so exceptions are awaited/logged/propagated intentionally.

### High Priority
1. **Duplicate-final suppression drops legitimate repeated questions for the entire session**  
   - Files: `/Users/february10/Documents/interviewCopilot/agent/message_router.py:34-38`, `/Users/february10/Documents/interviewCopilot/agent/runtime_state.py:32-38`  
   - Problem: duplicate detection stores one lowercase fingerprint indefinitely. If a user asks the same question twice later in the interview, the second `transcript.final` and `intent.detected` events are silently discarded.  
   - Impact: valid user input disappears with no error, which is especially likely in interviews where candidates restate or repeat prompts.  
   - Fix: scope dedupe to a short window / event id / provider sequence number instead of the entire session.

2. **Primary-to-fallback switchover does not replay the chunk that triggered fallback**  
   - File: `/Users/february10/Documents/interviewCopilot/agent/main.py:48-58`  
   - Problem: when primary returns error, code switches `active_provider` to fallback and returns, but the audio chunk that caused the failure is never retried on fallback.  
   - Impact: first utterance after timeout/failure can be truncated or lost. In the current baseline audio provider only emits once, so fallback may never receive any audio at all.  
   - Fix: preserve/replay the failed chunk on switchover, or let the capture pipeline fan out through a retryable buffer.

3. **Deepgram/local providers are static stubs that emit canned transcripts on every chunk**  
   - Files: `/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py:38-52`, `/Users/february10/Documents/interviewCopilot/agent/asr_local_fallback.py:33-47`  
   - Problem: providers ignore audio content and always emit the same partial/final transcript pair for every non-empty chunk.  
   - Impact: phase plan says “real audio” outputs; current implementation cannot satisfy that contract in runtime, and repeated chunks will spam identical final text until dedupe suppresses them.  
   - Fix: either integrate the real provider/client path or clearly gate these modules behind explicit dev-only simulation mode.

### Medium Priority
1. **Startup error status leaks internal exception class names to clients**  
   - File: `/Users/february10/Documents/interviewCopilot/agent/main.py:101-104`  
   - Problem: status update emits `Startup error: {type(exc).__name__}`.  
   - Impact: this exposes internal implementation detail to external consumers and is looser than `/Users/february10/Documents/interviewCopilot/shared/config-contracts.md:46-50`, which requires redaction of stack internals and secret-bearing failures.  
   - Fix: send stable error taxonomy/code only; keep exception class names in local logs.

2. **Bool parsing error message is contract-misleading for non-ZERO_STORAGE flags**  
   - File: `/Users/february10/Documents/interviewCopilot/agent/config.py:30-44`  
   - Problem: `_to_bool()` raises `ZERO_STORAGE_MODE must be one of...` even when parsing `ASR_FALLBACK_ENABLED`, `LANGUAGE_DETECTION_ENABLED`, `TRANSLATION_ENABLED`, or `INTENT_LLM_ASSIST_ENABLED`.  
   - Impact: operators get misleading startup diagnostics; this is a config-contract usability mismatch with `/Users/february10/Documents/interviewCopilot/shared/config-contracts.md:44`.  
   - Fix: pass the variable name into `_to_bool()` so validation errors point at the actual failing env var.

3. **Configured provider selector is validated but not actually honored at runtime**  
   - Files: `/Users/february10/Documents/interviewCopilot/agent/config.py:116-117`, `/Users/february10/Documents/interviewCopilot/agent/main.py:27,37`  
   - Problem: config carries `ASR_PRIMARY_PROVIDER`, but runtime hardcodes `deepgram-primary` state and constructs `DeepgramASRProvider()` directly.  
   - Impact: future additive contract changes become harder; current behavior makes the selector effectively dead config.  
   - Fix: route provider creation/state naming through one factory even if phase-04 only allows `deepgram`.

### Low Priority
1. **Translation toggle exists in config but Phase 04 pipeline does not use it**  
   - Files: `/Users/february10/Documents/interviewCopilot/agent/config.py:92`, `/Users/february10/Documents/interviewCopilot/agent/language_and_intent_pipeline.py:59-70`  
   - Note: shared contract says translation is no-op in Phase 04 baseline, so this is not a strict blocker. Still, the phase plan claims an optional translation path was implemented; code currently only detects language and intent.

2. **No formal tests cover the reviewed modules**  
   - Reference: `/Users/february10/Documents/interviewCopilot/plans/reports/tester-2026-04-23-phase-04-asr-language-intent.md:13-18`  
   - Impact: concurrency and session-lifecycle bugs above are exactly the kind of issues that smoke validation will miss.

### Contract Consistency Check
- `/Users/february10/Documents/interviewCopilot/.env.example` matches the variable set in `/Users/february10/Documents/interviewCopilot/shared/config-contracts.md:13-31`.
- `/Users/february10/Documents/interviewCopilot/agent/config.py:97-120` enforces port range, local host restriction, non-empty default language, positive audio settings, `deepgram` provider only, and positive ASR timeout as required.
- Mismatches / weak spots:
  - `/Users/february10/Documents/interviewCopilot/agent/config.py:30-44` returns the wrong variable name in bool parse errors.
  - `/Users/february10/Documents/interviewCopilot/agent/main.py:101-104` exposes exception class names to clients instead of stable redacted errors.
  - `/Users/february10/Documents/interviewCopilot/agent/config.py:107-120` does not fail startup on empty `AUDIO_DEVICE_NAME`; contract says it “should be non-empty for deterministic audio probe behavior”. Current behavior defers failure to runtime probe.

### Edge Cases Found by Scout
- Long-running session crosses `ASR_PRIMARY_TIMEOUT_MS` and starts timing out forever.
- Provider emits partial + final synchronously; task scheduling can reorder handling or drop exception visibility.
- Candidate repeats the same question later; dedupe suppresses legitimate final/intent events.
- Fallback activates on provider error but receives no replay of triggering audio chunk.

### Positive Observations
- `/Users/february10/Documents/interviewCopilot/agent/config.py:97-120` has solid startup boundary validation for host/port/provider/timeouts.
- `/Users/february10/Documents/interviewCopilot/agent/message_router.py:10-16` attempts to sanitize error messages before broadcasting.
- `/Users/february10/Documents/interviewCopilot/agent/ws_hub.py:116-124` restricts websocket peers to local/origin-checked clients, which is a good trust-boundary default.

### Recommended Actions
1. Fix timeout semantics in `/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py` so healthy sessions do not self-expire.
2. Serialize ASR result processing in `/Users/february10/Documents/interviewCopilot/agent/main.py` and make callback task failures explicit.
3. Replace session-wide transcript dedupe with bounded/event-aware dedupe.
4. Replay buffered audio on fallback switchover and test the first-failure handoff path.
5. Tighten client-facing error payloads and boolean parse diagnostics for config contract clarity.
6. Add focused unit/async tests for timeout, ordering, duplicate suppression, and fallback handoff before phase promotion.

### Gate Verdict
- **FAIL**
- Reason: blocking correctness/reliability issues remain in realtime event ordering, timeout behavior, and duplicate suppression. These are production-path bugs, not style issues.

### Metrics
- Type Coverage: N/A (Python; no typed coverage report present)
- Test Coverage: no formal Phase 04 coverage found for reviewed modules
- Linting Issues: not measured in this review

### Unresolved Questions
- Is Phase 04 intended to ship only simulation stubs, or should these ASR modules already process real provider/local audio?
- Should intentional duplicate questions later in a session be allowed through as distinct events?
