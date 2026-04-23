# Phase 04 QA Gate Rerun — ASR / language / intent

Date: 2026-04-23
Work context: `/Users/february10/Documents/interviewCopilot`
Scope: `/Users/february10/Documents/interviewCopilot/agent/asr_provider.py`, `/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py`, `/Users/february10/Documents/interviewCopilot/agent/asr_local_fallback.py`, `/Users/february10/Documents/interviewCopilot/agent/language_and_intent_pipeline.py`, `/Users/february10/Documents/interviewCopilot/agent/message_router.py`, `/Users/february10/Documents/interviewCopilot/agent/main.py`, `/Users/february10/Documents/interviewCopilot/agent/config.py`, `/Users/february10/Documents/interviewCopilot/agent/runtime_state.py`

## Diff-aware mode
Diff-aware mode: analyzed 8 changed files
  Changed: `/Users/february10/Documents/interviewCopilot/agent/asr_provider.py`, `/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py`, `/Users/february10/Documents/interviewCopilot/agent/asr_local_fallback.py`, `/Users/february10/Documents/interviewCopilot/agent/language_and_intent_pipeline.py`, `/Users/february10/Documents/interviewCopilot/agent/message_router.py`, `/Users/february10/Documents/interviewCopilot/agent/main.py`, `/Users/february10/Documents/interviewCopilot/agent/config.py`, `/Users/february10/Documents/interviewCopilot/agent/runtime_state.py`
  Mapped: none
  Unmapped: all scoped files; no formal Python test files discovered

[!] No tests found for `/Users/february10/Documents/interviewCopilot/agent/asr_provider.py` — consider unit tests for callback contract, empty chunk no-op, result shape
[!] No tests found for `/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py` — consider unit tests for timeout emission, elapsed timeout path, normal partial/final emission
[!] No tests found for `/Users/february10/Documents/interviewCopilot/agent/asr_local_fallback.py` — consider unit tests for fallback partial/final path and fail_mode error path
[!] No tests found for `/Users/february10/Documents/interviewCopilot/agent/language_and_intent_pipeline.py` — consider unit tests for normalization, Vietnamese detection, intent precedence, keyword extraction
[!] No tests found for `/Users/february10/Documents/interviewCopilot/agent/message_router.py` — consider async tests for queued ordering, duplicate final suppression, safe error payloads
[!] No tests found for `/Users/february10/Documents/interviewCopilot/agent/main.py` — consider async integration tests for fallback switchover, replayed buffered chunks, cleanup, startup failure
[!] No tests found for `/Users/february10/Documents/interviewCopilot/agent/config.py` — consider unit tests for env parsing and validation errors
[!] No tests found for `/Users/february10/Documents/interviewCopilot/agent/runtime_state.py` — consider unit tests for duplicate window timing and normalized fingerprint behavior

## Commands run
1. Syntax compile
   - `python3 -m py_compile "/Users/february10/Documents/interviewCopilot/agent/asr_provider.py" "/Users/february10/Documents/interviewCopilot/agent/asr_deepgram.py" "/Users/february10/Documents/interviewCopilot/agent/asr_local_fallback.py" "/Users/february10/Documents/interviewCopilot/agent/language_and_intent_pipeline.py" "/Users/february10/Documents/interviewCopilot/agent/message_router.py" "/Users/february10/Documents/interviewCopilot/agent/main.py" "/Users/february10/Documents/interviewCopilot/agent/config.py" "/Users/february10/Documents/interviewCopilot/agent/runtime_state.py" "/Users/february10/Documents/interviewCopilot/agent/ws_hub.py" "/Users/february10/Documents/interviewCopilot/agent/audio_capture.py"`
   - Result: PASS

2. Import validation
   - `python3 - <<'PY'
import sys
sys.path.insert(0, "/Users/february10/Documents/interviewCopilot/agent")
modules = [
    "asr_provider",
    "asr_deepgram",
    "asr_local_fallback",
    "language_and_intent_pipeline",
    "message_router",
    "main",
    "config",
    "runtime_state",
]
for name in modules:
    __import__(name)
    print(f"IMPORTED {name}")
PY`
   - Result: PASS
   - Output:
     - `IMPORTED asr_provider`
     - `IMPORTED asr_deepgram`
     - `IMPORTED asr_local_fallback`
     - `IMPORTED language_and_intent_pipeline`
     - `IMPORTED message_router`
     - `IMPORTED main`
     - `IMPORTED config`
     - `IMPORTED runtime_state`

3. Formal test discovery
   - `python3 -m unittest discover -s "/Users/february10/Documents/interviewCopilot" -p "test*.py"`
   - Result: no discovered tests
   - Output:
     - `Ran 0 tests in 0.000s`
     - `NO TESTS RAN`

4. Focused smoke: fallback switchover primitive behavior
   - `python3 - <<'PY'
import sys
sys.path.insert(0, "/Users/february10/Documents/interviewCopilot/agent")

from asr_deepgram import DeepgramASRProvider
from asr_local_fallback import LocalFallbackASRProvider
from asr_provider import ASRResult

captured = []

def cb(item: ASRResult):
    captured.append((item.kind, item.text, item.language, item.error_code))

primary = DeepgramASRProvider(timeout_ms=3000, force_timeout=True)
fallback = LocalFallbackASRProvider()
primary.start(cb)
fallback.start(cb)

primary.push_audio(b"chunk-1")
if captured[-1][0] == "error" and captured[-1][3] == "ASR_PRIMARY_TIMEOUT":
    fallback.push_audio(b"chunk-1")

print("CAPTURED", captured)
print("PRIMARY_TIMEOUT_ERROR", captured[0][0] == "error" and captured[0][3] == "ASR_PRIMARY_TIMEOUT")
print("FALLBACK_SEQUENCE", [item[0] for item in captured[1:]] == ["partial", "final"])
PY`
   - Result: PASS
   - Output summary:
     - primary emitted `ASR_PRIMARY_TIMEOUT`
     - fallback emitted `partial` then `final`

5. Focused smoke: queued ASR result processing ordering
   - `python3 - <<'PY'
import sys, asyncio
sys.path.insert(0, "/Users/february10/Documents/interviewCopilot/agent")

from asr_provider import ASRResult
from config import AgentConfig
from message_router import route_asr_result
from runtime_state import RuntimeState

class Hub:
    def __init__(self):
        self.events = []
    async def broadcast(self, event_type, payload):
        self.events.append((event_type, payload))

config = AgentConfig(
    deepgram_key=None,
    anthropic_key=None,
    whisper_api_key=None,
    translation_api_key=None,
    ws_host="127.0.0.1",
    ws_port=8765,
    default_language="auto",
    zero_storage_mode=True,
    audio_device_name="BlackHole",
    audio_sample_rate=16000,
    audio_chunk_ms=250,
    asr_primary_provider="deepgram",
    asr_fallback_enabled=True,
    asr_primary_timeout_ms=3000,
    language_detection_enabled=True,
    translation_enabled=False,
    intent_llm_assist_enabled=False,
)
state = RuntimeState()
hub = Hub()

async def main():
    queue = asyncio.Queue()
    await queue.put(ASRResult(kind="partial", text="first partial", language="en"))
    await queue.put(ASRResult(kind="final", text="Explain Selenium bug", language="en", confidence=0.91))
    await queue.put(ASRResult(kind="final", text="Explain Selenium bug", language="en", confidence=0.91))
    processed = []
    while not queue.empty():
        item = await queue.get()
        processed.append((item.kind, item.text))
        await route_asr_result(item, hub, state, config)
        queue.task_done()
    print("PROCESSED", processed)
    print("EVENTS", hub.events)
    print("ORDER_OK", [e[0] for e in hub.events] == ["transcript.partial", "transcript.final", "intent.detected"])
    print("DUPLICATE_SUPPRESSED", len([e for e in hub.events if e[0] == "transcript.final"]) == 1)

asyncio.run(main())
PY`
   - Result: PASS
   - Output summary:
     - processed queue order preserved: partial -> final -> duplicate final
     - emitted event order preserved: `transcript.partial` -> `transcript.final` -> `intent.detected`
     - duplicate final suppressed

6. Focused smoke: duplicate transcript suppression window behavior
   - `python3 - <<'PY'
import sys
sys.path.insert(0, "/Users/february10/Documents/interviewCopilot/agent")

from runtime_state import RuntimeState

state = RuntimeState(duplicate_window_ms=1200)
text = "Can you explain page object model?"

before = state.is_duplicate_final_transcript(text)
state.remember_final_transcript(text)
immediate = state.is_duplicate_final_transcript(text)
state.last_final_transcript_at_ms -= 1301
expired = state.is_duplicate_final_transcript(text)
casefold = state.is_duplicate_final_transcript("  can you EXPLAIN page object model?  ")

print("BEFORE_REMEMBER", before)
print("IMMEDIATE_DUPLICATE", immediate)
print("EXPIRED_WINDOW", expired)
print("NORMALIZED_MATCH_AFTER_EXPIRY", casefold)
PY`
   - Result: PASS
   - Output summary:
     - before remember: not duplicate
     - immediate same text: duplicate
     - after window expiry: not duplicate
     - normalized same text after expiry: not duplicate, as expected

7. In-process runtime smoke via `main.run()` with stubs
   - `python3 - <<'PY'
import sys, asyncio
sys.path.insert(0, "/Users/february10/Documents/interviewCopilot/agent")

import main as agent_main
from asr_provider import ASRResult
from audio_capture import AudioProbeResult
from config import AgentConfig

class StubHub:
    instances = []
    def __init__(self, host, port, session_id, state_provider=None):
        self.host = host
        self.port = port
        self.session_id = session_id
        self.state_provider = state_provider
        self.events = []
        self.started = False
        self.stopped = False
        StubHub.instances.append(self)
    async def start(self):
        self.started = True
    async def broadcast(self, event_type, payload):
        self.events.append((event_type, payload))
    async def wait_forever(self):
        await asyncio.sleep(0.05)
    async def stop(self):
        self.stopped = True

class StubCapture:
    instances = []
    def __init__(self, config):
        self.config = config
        self.started = False
        self.stopped = False
        StubCapture.instances.append(self)
    def probe(self):
        return AudioProbeResult(available=True, provider="stub-loopback", details="ready")
    def start(self, on_chunk):
        self.started = True
        on_chunk(b"audio-1")
    def stop(self):
        self.stopped = True

class StubPrimary:
    instances = []
    def __init__(self, timeout_ms):
        self.timeout_ms = timeout_ms
        self.callback = None
        self.closed = False
        StubPrimary.instances.append(self)
    def start(self, callback):
        self.callback = callback
    def push_audio(self, chunk):
        self.callback(ASRResult(kind="error", text="", error_code="ASR_PRIMARY_TIMEOUT"))
    def close(self):
        self.closed = True

class StubFallback:
    instances = []
    def __init__(self):
        self.callback = None
        self.closed = False
        self.received = []
        StubFallback.instances.append(self)
    def start(self, callback):
        self.callback = callback
    def push_audio(self, chunk):
        self.received.append(chunk)
        self.callback(ASRResult(kind="partial", text="fallback partial", language="en"))
        self.callback(ASRResult(kind="final", text="Fallback final answer", language="en", confidence=0.5))
    def close(self):
        self.closed = True


def load_cfg():
    return AgentConfig(
        deepgram_key=None,
        anthropic_key=None,
        whisper_api_key=None,
        translation_api_key=None,
        ws_host="127.0.0.1",
        ws_port=8765,
        default_language="auto",
        zero_storage_mode=True,
        audio_device_name="BlackHole",
        audio_sample_rate=16000,
        audio_chunk_ms=250,
        asr_primary_provider="deepgram",
        asr_fallback_enabled=True,
        asr_primary_timeout_ms=3000,
        language_detection_enabled=True,
        translation_enabled=False,
        intent_llm_assist_enabled=False,
    )

agent_main.WebSocketHub = StubHub
agent_main.AudioCaptureProvider = StubCapture
agent_main.DeepgramASRProvider = StubPrimary
agent_main.LocalFallbackASRProvider = StubFallback
agent_main.load_agent_config = load_cfg
agent_main.validate_startup_config = lambda config: None

async def run_test():
    await agent_main.run()
    hub = StubHub.instances[0]
    fallback = StubFallback.instances[0]
    capture = StubCapture.instances[0]
    primary = StubPrimary.instances[0]
    print("EVENTS", hub.events)
    print("HAS_SWITCH", any(e[0] == "status.update" and e[1].get("message") == "Switching to fallback ASR" for e in hub.events))
    print("HAS_FINAL", any(e[0] == "transcript.final" and e[1].get("text") == "Fallback final answer" for e in hub.events))
    print("HAS_INTENT", any(e[0] == "intent.detected" for e in hub.events))
    print("FALLBACK_REPLAYED_BUFFER", fallback.received == [b"audio-1"])
    print("CLEANUP", capture.stopped and primary.closed and fallback.closed and hub.stopped)

asyncio.run(run_test())
PY`
   - Result: PASS
   - Output summary:
     - startup and audio-ready statuses emitted
     - fallback switch emitted after primary timeout
     - replayed buffered audio chunk reached fallback provider
     - final transcript and intent emitted after switchover
     - capture/provider/hub cleanup executed

## Test Results Overview
- Formal tests run: 0
- Smoke validations run: 4 focused checks
- Passed: 4 focused checks + syntax compile + import validation
- Failed: 0 behavioral checks
- Skipped: none
- Diff-based total: `Ran 0/0 tests (diff-based): 0 passed, 0 failed`

## Coverage Metrics
- Line coverage: not available
- Branch coverage: not available
- Function coverage: not available
- Reason: no formal Python tests or coverage tooling configured in repo for this scope

## Failed Tests
- None
- Gap only: `unittest discover` found no tests

## Performance Metrics
- No benchmark suite present
- All smoke scripts completed quickly within shell timeout
- No hangs observed; runtime smoke used stubbed `wait_forever()` sleep to exit deterministicly

## Build Status
- Syntax/import status: PASS
- Scoped runtime smoke status: PASS
- Warnings:
  - no formal Python tests exist for scoped files
  - no coverage report available
  - imports depend on `agent/` being added to `sys.path`

## Critical Issues
- No blocking runtime regressions found in requested Phase 04 scope
- Quality gap remains: missing formal automated tests and coverage for Phase 04 modules

## Recommendations
1. Add unit tests for `/Users/february10/Documents/interviewCopilot/agent/runtime_state.py` duplicate window boundaries and normalization semantics.
2. Add async tests for `/Users/february10/Documents/interviewCopilot/agent/message_router.py` event ordering and duplicate suppression under repeated final transcripts.
3. Add integration tests for `/Users/february10/Documents/interviewCopilot/agent/main.py` fallback switchover and replay buffer behavior using stubs similar to this smoke.
4. Add coverage command and threshold before later phase promotion.

## Next Steps
1. Accept Phase 04 rerun gate as PASS for runtime verification.
2. Before Phase 05/07 hardening, add formal Python tests for scoped files.
3. Add coverage reporting so future gate reruns can include hard metrics.

## Gate verdict
PASS

Reason: scoped files compile, import, and pass targeted runtime smoke checks for fallback switchover, queued ASR result ordering, and duplicate transcript suppression window behavior. Confidence medium due to lack of formal automated tests.

## Unresolved questions
- Should Phase 04 promotion require a minimum Python unit-test baseline, or is smoke-only acceptable for this phase rerun?
- Should these agent modules be package-qualified to avoid manual `sys.path` injection during validation?
