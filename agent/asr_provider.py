from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Callable


@dataclass(frozen=True)
class ASRResult:
    kind: str
    text: str
    language: str | None = None
    confidence: float | None = None
    error_code: str | None = None
    error_stage: str | None = None


ASRCallback = Callable[[ASRResult], None]


class ASRProvider(Protocol):
    name: str

    def start(self, callback: ASRCallback) -> None: ...

    def push_audio(self, chunk: bytes) -> None: ...

    def close(self) -> None: ...
