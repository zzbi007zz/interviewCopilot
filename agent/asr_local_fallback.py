from __future__ import annotations

from dataclasses import dataclass

from asr_provider import ASRProvider, ASRCallback, ASRResult


@dataclass
class LocalFallbackASRProvider(ASRProvider):
    fail_mode: bool = False

    def __post_init__(self) -> None:
        self.name = "local-fallback"
        self._callback: ASRCallback | None = None

    def start(self, callback: ASRCallback) -> None:
        self._callback = callback

    def push_audio(self, chunk: bytes) -> None:
        if self._callback is None or not chunk:
            return

        if self.fail_mode:
            self._callback(
                ASRResult(
                    kind="error",
                    text="",
                    error_code="ASR_FALLBACK_UNAVAILABLE",
                    error_stage="asr-fallback",
                )
            )
            return

        self._callback(
            ASRResult(
                kind="partial",
                text="fallback transcript partial",
                language="en",
            )
        )
        self._callback(
            ASRResult(
                kind="final",
                text="Fallback transcript final",
                language="en",
                confidence=0.6,
            )
        )

    def close(self) -> None:
        self._callback = None
