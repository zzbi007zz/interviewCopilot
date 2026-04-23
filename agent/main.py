from __future__ import annotations

import asyncio
import contextlib
from collections import deque

from audio_capture import AudioCaptureProvider
from asr_deepgram import DeepgramASRProvider
from asr_local_fallback import LocalFallbackASRProvider
from asr_provider import ASRResult
from config import load_agent_config, validate_startup_config
from message_router import ERROR_TAXONOMY, route_asr_result
from runtime_state import RuntimeState
from ws_hub import WebSocketHub


async def run() -> None:
    state = RuntimeState()
    hub: WebSocketHub | None = None
    capture: AudioCaptureProvider | None = None
    primary = None
    fallback = None
    result_worker_task: asyncio.Task[None] | None = None

    try:
        config = load_agent_config()
        validate_startup_config(config)

        state.set_status("listening")
        state.set_active_provider("deepgram-primary")

        hub = WebSocketHub(
            config.ws_host,
            config.ws_port,
            state.session_id,
            state_provider=lambda: state.current_status,
        )
        capture = AudioCaptureProvider(config)

        primary = DeepgramASRProvider(timeout_ms=config.asr_primary_timeout_ms)
        fallback = LocalFallbackASRProvider()

        async def broadcast_health(message: str | None = None) -> None:
            diagnostics = state.diagnostics_snapshot()
            if message:
                diagnostics["message"] = message
            await hub.broadcast("health.diagnostics", diagnostics)

        await hub.start()
        await hub.broadcast(
            "status.update",
            {"state": state.current_status, "message": "Agent started"},
            metadata={
                "provider": state.active_asr_provider,
                "fallbackActive": state.fallback_active,
                "audioReady": state.audio_ready,
                "zeroStorageMode": config.zero_storage_mode,
            },
        )
        await broadcast_health("startup-complete")

        active_provider = primary
        recent_audio_chunks: deque[bytes] = deque(maxlen=4)
        asr_result_queue: asyncio.Queue[ASRResult] = asyncio.Queue()

        async def handle_asr_result(result: ASRResult) -> None:
            nonlocal active_provider

            if result.kind == "error" and active_provider is primary and config.asr_fallback_enabled:
                state.mark_fallback_active(True)
                state.set_active_provider("local-fallback")
                state.set_status("processing")
                await hub.broadcast(
                    "status.update",
                    {"state": state.current_status, "message": "Switching to fallback ASR"},
                )
                await broadcast_health("fallback-activated")
                active_provider = fallback
                fallback.start(lambda item: asr_result_queue.put_nowait(item))
                for buffered_chunk in list(recent_audio_chunks):
                    active_provider.push_audio(buffered_chunk)
                return

            await route_asr_result(result, hub, state, config)
            await broadcast_health()

        async def process_asr_results() -> None:
            while True:
                result = await asr_result_queue.get()
                try:
                    await handle_asr_result(result)
                except Exception:
                    state.set_status("error")
                    state.remember_error("ASR_PIPELINE_FAILURE", "pipeline", True)
                    await hub.broadcast(
                        "error",
                        {
                            "code": "ASR_PIPELINE_FAILURE",
                            "message": "ASR pipeline failed",
                            "retryable": True,
                            "stage": "pipeline",
                        },
                    )
                    await broadcast_health("pipeline-error")
                finally:
                    asr_result_queue.task_done()

        result_worker_task = asyncio.create_task(process_asr_results())
        primary.start(lambda item: asr_result_queue.put_nowait(item))

        probe_result = capture.probe()
        if probe_result.available:
            state.mark_audio_ready(True)
            state.set_status("processing")
            await hub.broadcast(
                "status.update",
                {"state": state.current_status, "message": f"Audio ready via {probe_result.provider}"},
            )
            await broadcast_health("audio-ready")
            def on_audio_chunk(chunk: bytes) -> None:
                recent_audio_chunks.append(chunk)
                active_provider.push_audio(chunk)

            capture.start(on_audio_chunk)
        else:
            state.mark_audio_ready(False)
            state.set_status("error")
            state.remember_error("AUDIO_DEVICE_NOT_READY", "audio-capture", True)
            await hub.broadcast(
                "error",
                {
                    "code": "AUDIO_DEVICE_NOT_READY",
                    "message": "Audio capture device is unavailable",
                    "retryable": True,
                    "stage": "audio-capture",
                },
            )
            await hub.broadcast(
                "status.update",
                {"state": state.current_status, "message": probe_result.details},
            )
            await broadcast_health("audio-unavailable")

        await hub.wait_forever()
    except Exception:
        state.set_status("error")
        state.remember_error("AGENT_STARTUP_FAILURE", "startup", False)
        if hub is not None:
            await hub.broadcast(
                "error",
                {
                    "code": "AGENT_STARTUP_FAILURE",
                    "message": "Agent startup failed",
                    "retryable": False,
                    "stage": "startup",
                },
            )
            await hub.broadcast(
                "status.update",
                {"state": state.current_status, "message": "Startup error"},
            )
            diagnostics = state.diagnostics_snapshot()
            diagnostics["message"] = "startup-error"
            await hub.broadcast("health.diagnostics", diagnostics)
        raise
    finally:
        if capture is not None:
            capture.stop()
        if primary is not None:
            primary.close()
        if fallback is not None:
            fallback.close()
        if result_worker_task is not None:
            result_worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await result_worker_task
        if hub is not None:
            await hub.stop()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
