from __future__ import annotations

from dataclasses import dataclass
import re

from config import AgentConfig


@dataclass(frozen=True)
class PipelineOutput:
    normalized_text: str
    language: str
    question_type: str
    keywords: list[str]


_RULES: list[tuple[str, str]] = [
    (r"\b(explain|what is|difference|how does)\b", "conceptual"),
    (r"\b(fix|bug|error|fail|broken)\b", "debugging"),
    (r"\b(test|selenium|playwright|api|ci/cd)\b", "qa-automation"),
]


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def _detect_language(text: str, config: AgentConfig) -> str:
    if not config.language_detection_enabled:
        return config.default_language

    if any(char in text for char in "ăâđêôơưÁÀẢÃẠáàảãạ"):
        return "vi"

    return "en" if text else config.default_language


def _extract_keywords(text: str) -> list[str]:
    lowered = text.lower()
    keywords: list[str] = []
    for token in ["page object model", "selenium", "playwright", "api", "ci/cd", "bug"]:
        if token in lowered:
            keywords.append(token)
    return keywords


def _classify_intent(text: str, config: AgentConfig) -> str:
    lowered = text.lower()
    for pattern, intent in _RULES:
        if re.search(pattern, lowered):
            return intent

    if config.intent_llm_assist_enabled:
        return "unknown"

    return "unknown"


def process_final_transcript(text: str, config: AgentConfig) -> PipelineOutput:
    normalized = _normalize_text(text)
    language = _detect_language(normalized, config)
    keywords = _extract_keywords(normalized)
    question_type = _classify_intent(normalized, config)

    return PipelineOutput(
        normalized_text=normalized,
        language=language,
        question_type=question_type,
        keywords=keywords,
    )
