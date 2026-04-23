from __future__ import annotations

from answer_orchestrator import generate_answer_payload
from asr_provider import ASRResult
from config import AgentConfig
from language_and_intent_pipeline import process_final_transcript
from runtime_state import RuntimeState
from ws_hub import WebSocketHub

ERROR_TAXONOMY: dict[str, dict[str, str | bool]] = {
    "ASR_PRIMARY_TIMEOUT": {
        "message": "Primary ASR timed out",
        "stage": "asr-primary",
        "retryable": True,
    },
    "ASR_FALLBACK_UNAVAILABLE": {
        "message": "Fallback ASR unavailable",
        "stage": "asr-fallback",
        "retryable": True,
    },
    "ASR_PIPELINE_FAILURE": {
        "message": "ASR pipeline failed",
        "stage": "pipeline",
        "retryable": True,
    },
    "AUDIO_DEVICE_NOT_READY": {
        "message": "Audio capture device is unavailable",
        "stage": "audio-capture",
        "retryable": True,
    },
    "AGENT_STARTUP_FAILURE": {
        "message": "Agent startup failed",
        "stage": "startup",
        "retryable": False,
    },
    "ANSWER_GENERATION_FAILURE": {
        "message": "Answer generation failed",
        "stage": "answer-generation",
        "retryable": True,
    },
    "ASR_ERROR": {
        "message": "ASR provider failure",
        "stage": "asr-primary",
        "retryable": True,
    },
}


def _safe_error_message(message: str) -> str:
    lowered = message.lower()
    for marker in ("api_key", "secret", "authorization", "traceback", "stack"):
        if marker in lowered:
            return "ASR pipeline error"
    return message or "ASR pipeline error"


def _resolve_error_details(
    code: str | None,
    stage: str | None = None,
) -> tuple[str, str, bool]:
    resolved_code = code or "ASR_ERROR"
    details = ERROR_TAXONOMY.get(resolved_code, ERROR_TAXONOMY["ASR_ERROR"])
    message = _safe_error_message(str(details["message"]))
    resolved_stage = stage or str(details["stage"])
    retryable = bool(details["retryable"])
    return resolved_code, resolved_stage, retryable


async def route_asr_result(
    result: ASRResult,
    hub: WebSocketHub,
    state: RuntimeState,
    config: AgentConfig,
) -> None:
    diagnostics_metadata = {
        "provider": state.active_asr_provider,
        "fallbackActive": state.fallback_active,
        "audioReady": state.audio_ready,
        "zeroStorageMode": config.zero_storage_mode,
    }
    if result.kind == "partial":
        state.mark_partial_transcript()
        await hub.broadcast(
            "transcript.partial",
            {
                "text": result.text,
                "language": result.language or config.default_language,
            },
            metadata=diagnostics_metadata,
        )
        return

    if result.kind == "final":
        if state.is_duplicate_final_transcript(result.text):
            return

        state.remember_final_transcript(result.text)
        state.mark_final_transcript()
        await hub.broadcast(
            "transcript.final",
            {
                "text": result.text,
                "language": result.language or config.default_language,
                "confidence": result.confidence,
            },
            metadata=diagnostics_metadata,
        )

        pipeline = process_final_transcript(result.text, config)
        await hub.broadcast(
            "intent.detected",
            {
                "questionType": pipeline.question_type,
                "keywords": pipeline.keywords,
                "language": pipeline.language,
            },
            metadata=diagnostics_metadata,
        )

        try:
            answer = await generate_answer_payload(result.text, pipeline, config)
        except Exception:
            code, stage, retryable = _resolve_error_details("ANSWER_GENERATION_FAILURE")
            state.remember_error(code, stage, retryable)
            await hub.broadcast(
                "error",
                {
                    "code": code,
                    "message": ERROR_TAXONOMY[code]["message"],
                    "retryable": retryable,
                    "stage": stage,
                },
                metadata=diagnostics_metadata,
            )
            return

        state.mark_answer_generated()
        await hub.broadcast(
            "answer.generated",
            {
                "sourceText": answer.source_text,
                "questionType": answer.question_type,
                "optionA": answer.option_a,
                "optionB": answer.option_b,
                "language": answer.language,
                "fallbackUsed": answer.fallback_used,
                "qcStatus": answer.qc_status,
            },
            metadata=diagnostics_metadata,
        )
        return

    if result.kind == "error":
        code, stage, retryable = _resolve_error_details(result.error_code, result.error_stage)
        state.remember_error(code, stage, retryable)
        await hub.broadcast(
            "error",
            {
                "code": code,
                "message": ERROR_TAXONOMY.get(code, ERROR_TAXONOMY["ASR_ERROR"])["message"],
                "retryable": retryable,
                "stage": stage,
            },
            metadata=diagnostics_metadata,
        )
