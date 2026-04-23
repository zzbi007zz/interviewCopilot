from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from asr_provider import ASRProvider, ASRCallback, ASRResult


@dataclass
class DeepgramASRProvider(ASRProvider):
    timeout_ms: int
    force_timeout: bool = False

    def __post_init__(self) -> None:
        self.name = "deepgram-primary"
        self._callback: ASRCallback | None = None
        self._last_activity_at = 0.0

    def start(self, callback: ASRCallback) -> None:
        self._callback = callback
        self._last_activity_at = monotonic()

    def push_audio(self, chunk: bytes) -> None:
        if self._callback is None or not chunk:
            return

        now = monotonic()
        elapsed_ms = (now - self._last_activity_at) * 1000
        if self.force_timeout or elapsed_ms > self.timeout_ms:
            self._callback(
                ASRResult(
                    kind="error",
                    text="",
                    error_code="ASR_PRIMARY_TIMEOUT",
                    error_stage="asr-primary",
                )
            )
            self._last_activity_at = now
            return

        self._last_activity_at = now

        self._callback(
            ASRResult(
                kind="partial",
                text="explain page object model",
                language="en",
            )
        )
        self._callback(
            ASRResult(
                kind="final",
                text="Can you explain page object model?",
                language="en",
                confidence=0.97,
            )
        )

    def close(self) -> None:
        self._callback = None
