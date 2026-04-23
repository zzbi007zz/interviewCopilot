from __future__ import annotations

import asyncio
from typing import Any

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


class AnswerClientError(Exception):
    pass


class AnthropicAnswerClient:
    def __init__(
        self,
        api_key: str | None,
        timeout_ms: int,
        max_tokens: int,
        model: str = DEFAULT_ANTHROPIC_MODEL,
    ) -> None:
        self._api_key = api_key.strip() if api_key else ""
        self._timeout_seconds = timeout_ms / 1000
        self._max_tokens = max_tokens
        self._model = model
        self._client = self._create_client()

    def _create_client(self) -> Any | None:
        if not self._api_key:
            return None

        try:
            from anthropic import AsyncAnthropic
        except Exception:
            return None

        return AsyncAnthropic(api_key=self._api_key)

    @property
    def available(self) -> bool:
        return self._client is not None

    async def generate_answer(self, prompt: str) -> str:
        if not self._api_key:
            raise AnswerClientError("ANSWER_PROVIDER_UNAVAILABLE")

        if self._client is None:
            raise AnswerClientError("ANSWER_PROVIDER_SDK_UNAVAILABLE")

        if not prompt.strip():
            raise AnswerClientError("ANSWER_PROMPT_EMPTY")

        try:
            response = await asyncio.wait_for(
                self._client.messages.create(
                    model=self._model,
                    max_tokens=self._max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=self._timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            raise AnswerClientError("ANSWER_PROVIDER_TIMEOUT") from exc
        except Exception as exc:
            raise AnswerClientError("ANSWER_PROVIDER_FAILURE") from exc

        output = self._extract_text(response)
        if not output:
            raise AnswerClientError("ANSWER_PROVIDER_EMPTY")
        return output

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", None)
        if not isinstance(content, list):
            return ""

        parts: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())

        return "\n".join(parts).strip()
