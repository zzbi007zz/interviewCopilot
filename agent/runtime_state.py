from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import monotonic
from typing import Any
import uuid


@dataclass
class RuntimeState:
    session_id: str = field(default_factory=lambda: f"session-{uuid.uuid4().hex[:12]}")
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    current_status: str = "idle"
    audio_ready: bool = False
    active_asr_provider: str = "deepgram-primary"
    fallback_active: bool = False
    last_error_code: str | None = None
    last_error_stage: str | None = None
    last_error_retryable: bool = False
    last_final_transcript_fingerprint: str | None = None
    last_final_transcript_at_ms: float = 0.0
    duplicate_window_ms: int = 1200
    partial_transcript_count: int = 0
    final_transcript_count: int = 0
    error_count: int = 0
    answer_count: int = 0
    last_partial_at: str | None = None
    last_final_at: str | None = None
    last_answer_at: str | None = None

    def set_status(self, status: str) -> None:
        self.current_status = status

    def mark_audio_ready(self, ready: bool) -> None:
        self.audio_ready = ready

    def set_active_provider(self, provider_name: str) -> None:
        self.active_asr_provider = provider_name

    def mark_fallback_active(self, active: bool) -> None:
        self.fallback_active = active

    def mark_partial_transcript(self) -> None:
        self.partial_transcript_count += 1
        self.last_partial_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_final_transcript(self) -> None:
        self.final_transcript_count += 1
        self.last_final_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_answer_generated(self) -> None:
        self.answer_count += 1
        self.last_answer_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def remember_error(self, code: str, stage: str, retryable: bool) -> None:
        self.last_error_code = code
        self.last_error_stage = stage
        self.last_error_retryable = retryable
        self.error_count += 1

    def diagnostics_snapshot(self) -> dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "startedAt": self.started_at,
            "state": self.current_status,
            "audioReady": self.audio_ready,
            "provider": self.active_asr_provider,
            "fallbackActive": self.fallback_active,
            "counts": {
                "partialTranscripts": self.partial_transcript_count,
                "finalTranscripts": self.final_transcript_count,
                "answers": self.answer_count,
                "errors": self.error_count,
            },
            "lastEvents": {
                "partialAt": self.last_partial_at,
                "finalAt": self.last_final_at,
                "answerAt": self.last_answer_at,
            },
            "lastError": {
                "code": self.last_error_code,
                "stage": self.last_error_stage,
                "retryable": self.last_error_retryable,
            },
        }

    def is_duplicate_final_transcript(self, text: str) -> bool:
        fingerprint = text.strip().lower()
        if not fingerprint:
            return False

        now_ms = monotonic() * 1000
        same_text = fingerprint == self.last_final_transcript_fingerprint
        within_window = (now_ms - self.last_final_transcript_at_ms) <= self.duplicate_window_ms
        return same_text and within_window

    def remember_final_transcript(self, text: str) -> None:
        fingerprint = text.strip().lower()
        self.last_final_transcript_fingerprint = fingerprint or None
        self.last_final_transcript_at_ms = monotonic() * 1000
