from __future__ import annotations

from dataclasses import dataclass

from answer_client import AnthropicAnswerClient, AnswerClientError
from answer_fallback import generate_fallback_answer
from answer_output_parser import parse_answer_output
from config import AgentConfig
from language_and_intent_pipeline import PipelineOutput
from qc_prompt_template import build_qc_prompt


@dataclass(frozen=True)
class AnswerPayload:
    source_text: str
    question_type: str
    option_a: list[str]
    option_b: list[str]
    language: str
    fallback_used: bool
    qc_status: str


def _normalize_language_code(language: str) -> str:
    return "vi" if language.strip().lower() == "vi" else "en"


async def generate_answer_payload(
    source_text: str,
    pipeline: PipelineOutput,
    config: AgentConfig,
) -> AnswerPayload:
    normalized_language = _normalize_language_code(pipeline.language)
    prompt = build_qc_prompt(
        source_text=source_text,
        language=normalized_language,
        question_type=pipeline.question_type,
        keywords=pipeline.keywords,
    )

    client = AnthropicAnswerClient(
        api_key=config.anthropic_key,
        timeout_ms=config.answer_provider_timeout_ms,
        max_tokens=config.answer_max_tokens,
    )

    try:
        raw_answer = await client.generate_answer(prompt)
        parsed = parse_answer_output(raw_answer)
        return AnswerPayload(
            source_text=source_text,
            question_type=pipeline.question_type,
            option_a=parsed.option_a,
            option_b=parsed.option_b,
            language=normalized_language,
            fallback_used=False,
            qc_status="passed",
        )
    except (AnswerClientError, ValueError):
        fallback = generate_fallback_answer(normalized_language, pipeline.question_type)
        return AnswerPayload(
            source_text=source_text,
            question_type=pipeline.question_type,
            option_a=fallback.option_a,
            option_b=fallback.option_b,
            language=fallback.language,
            fallback_used=True,
            qc_status="fallback",
        )
