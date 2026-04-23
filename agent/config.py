from __future__ import annotations

import os
from dataclasses import dataclass

PROTOCOL_VERSION = "1.0.0"


@dataclass(frozen=True)
class AgentConfig:
    deepgram_key: str | None
    anthropic_key: str | None
    whisper_api_key: str | None
    translation_api_key: str | None
    ws_host: str
    ws_port: int
    default_language: str
    zero_storage_mode: bool
    audio_device_name: str
    audio_sample_rate: int
    audio_chunk_ms: int
    asr_primary_provider: str
    asr_fallback_enabled: bool
    asr_primary_timeout_ms: int
    language_detection_enabled: bool
    translation_enabled: bool
    intent_llm_assist_enabled: bool
    answer_max_tokens: int
    answer_provider_timeout_ms: int


def _to_bool(value: str | None, default: bool, env_name: str) -> bool:
    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in {"1", "true", "yes", "on"}:
        return True

    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"{env_name} must be one of: 1,true,yes,on,0,false,no,off"
    )


def load_agent_config() -> AgentConfig:
    ws_port_raw = os.getenv("LOCAL_AGENT_WS_PORT", "8765")

    try:
        ws_port = int(ws_port_raw)
    except ValueError as exc:
        raise ValueError("LOCAL_AGENT_WS_PORT must be an integer") from exc

    ws_host = os.getenv("LOCAL_AGENT_WS_HOST", "127.0.0.1").strip()
    default_language = os.getenv("DEFAULT_LANGUAGE", "auto").strip()
    audio_device_name = os.getenv("AUDIO_DEVICE_NAME", "BlackHole").strip()

    try:
        audio_sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    except ValueError as exc:
        raise ValueError("AUDIO_SAMPLE_RATE must be an integer") from exc

    try:
        audio_chunk_ms = int(os.getenv("AUDIO_CHUNK_MS", "250"))
    except ValueError as exc:
        raise ValueError("AUDIO_CHUNK_MS must be an integer") from exc

    try:
        asr_primary_timeout_ms = int(os.getenv("ASR_PRIMARY_TIMEOUT_MS", "3000"))
    except ValueError as exc:
        raise ValueError("ASR_PRIMARY_TIMEOUT_MS must be an integer") from exc

    asr_primary_provider = os.getenv("ASR_PRIMARY_PROVIDER", "deepgram").strip().lower()

    try:
        answer_max_tokens = int(os.getenv("ANSWER_MAX_TOKENS", "200"))
    except ValueError as exc:
        raise ValueError("ANSWER_MAX_TOKENS must be an integer") from exc

    try:
        answer_provider_timeout_ms = int(os.getenv("ANSWER_PROVIDER_TIMEOUT_MS", "2500"))
    except ValueError as exc:
        raise ValueError("ANSWER_PROVIDER_TIMEOUT_MS must be an integer") from exc

    return AgentConfig(
        deepgram_key=os.getenv("DEEPGRAM_KEY"),
        anthropic_key=os.getenv("ANTHROPIC_KEY"),
        whisper_api_key=os.getenv("WHISPER_API_KEY"),
        translation_api_key=os.getenv("TRANSLATION_API_KEY"),
        ws_host=ws_host,
        ws_port=ws_port,
        default_language=default_language,
        zero_storage_mode=_to_bool(os.getenv("ZERO_STORAGE_MODE"), True, "ZERO_STORAGE_MODE"),
        audio_device_name=audio_device_name,
        audio_sample_rate=audio_sample_rate,
        audio_chunk_ms=audio_chunk_ms,
        asr_primary_provider=asr_primary_provider,
        asr_fallback_enabled=_to_bool(
            os.getenv("ASR_FALLBACK_ENABLED"), True, "ASR_FALLBACK_ENABLED"
        ),
        asr_primary_timeout_ms=asr_primary_timeout_ms,
        language_detection_enabled=_to_bool(
            os.getenv("LANGUAGE_DETECTION_ENABLED"), True, "LANGUAGE_DETECTION_ENABLED"
        ),
        translation_enabled=_to_bool(
            os.getenv("TRANSLATION_ENABLED"), False, "TRANSLATION_ENABLED"
        ),
        intent_llm_assist_enabled=_to_bool(
            os.getenv("INTENT_LLM_ASSIST_ENABLED"), False, "INTENT_LLM_ASSIST_ENABLED"
        ),
        answer_max_tokens=answer_max_tokens,
        answer_provider_timeout_ms=answer_provider_timeout_ms,
    )


def validate_startup_config(config: AgentConfig) -> None:
    if not config.ws_host:
        raise ValueError("LOCAL_AGENT_WS_HOST cannot be empty")

    if config.ws_host != "127.0.0.1" and config.ws_host != "localhost":
        raise ValueError("LOCAL_AGENT_WS_HOST must remain local by default")

    if config.ws_port <= 0 or config.ws_port > 65535:
        raise ValueError("LOCAL_AGENT_WS_PORT must be between 1 and 65535")

    if not config.default_language:
        raise ValueError("DEFAULT_LANGUAGE cannot be empty")

    if not config.audio_device_name:
        raise ValueError("AUDIO_DEVICE_NAME cannot be empty")

    if config.audio_sample_rate <= 0:
        raise ValueError("AUDIO_SAMPLE_RATE must be greater than 0")

    if config.audio_chunk_ms <= 0:
        raise ValueError("AUDIO_CHUNK_MS must be greater than 0")

    if config.asr_primary_provider not in {"deepgram"}:
        raise ValueError("ASR_PRIMARY_PROVIDER must be 'deepgram' in this phase")

    if config.asr_primary_timeout_ms <= 0:
        raise ValueError("ASR_PRIMARY_TIMEOUT_MS must be greater than 0")

    if config.answer_max_tokens <= 0:
        raise ValueError("ANSWER_MAX_TOKENS must be greater than 0")

    if config.answer_provider_timeout_ms <= 0:
        raise ValueError("ANSWER_PROVIDER_TIMEOUT_MS must be greater than 0")
