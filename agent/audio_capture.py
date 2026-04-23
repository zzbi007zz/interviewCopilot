from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import os

from config import AgentConfig


@dataclass(frozen=True)
class AudioProbeResult:
    available: bool
    provider: str
    details: str


class AudioCaptureProvider:
    def __init__(self, config: AgentConfig) -> None:
        self._config = config
        self._running = False

    def probe(self) -> AudioProbeResult:
        device = self._config.audio_device_name.strip()
        if not device:
            return AudioProbeResult(
                available=False,
                provider="loopback",
                details="AUDIO_DEVICE_NAME is empty",
            )

        if "blackhole" in device.lower():
            return AudioProbeResult(
                available=True,
                provider="blackhole-loopback",
                details=f"Configured device '{device}' accepted",
            )

        return AudioProbeResult(
            available=False,
            provider="loopback",
            details=(
                f"Configured device '{device}' not recognized for baseline runtime; "
                "set AUDIO_DEVICE_NAME=BlackHole to enable loopback baseline"
            ),
        )

    def start(self, on_chunk: Callable[[bytes], None]) -> None:
        self._running = True
        sample = os.urandom(32)
        on_chunk(sample)

    def stop(self) -> None:
        self._running = False

    @property
    def running(self) -> bool:
        return self._running
