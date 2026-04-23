from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ParsedAnswer:
    option_a: list[str]
    option_b: list[str]


def _extract_option_block(text: str, heading: str, next_heading: str | None) -> str:
    lowered = text.lower()
    heading_marker = f"{heading.lower()}:"
    start = lowered.find(heading_marker)
    if start < 0:
        raise ValueError(f"Missing section: {heading}")

    content_start = start + len(heading_marker)
    if next_heading is None:
        return text[content_start:]

    next_marker = f"{next_heading.lower()}:"
    next_index = lowered.find(next_marker, content_start)
    if next_index < 0:
        raise ValueError(f"Missing section: {next_heading}")
    return text[content_start:next_index]


_NUMBERED_BULLET_PATTERN = re.compile(r"^\d+\.\s+")


def _parse_bullets(block: str) -> list[str]:
    bullets: list[str] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        normalized = ""
        if line.startswith("- "):
            normalized = line[2:]
        elif line.startswith("*"):
            normalized = line[1:].strip()
        elif _NUMBERED_BULLET_PATTERN.match(line):
            normalized = _NUMBERED_BULLET_PATTERN.sub("", line, count=1)
        else:
            raise ValueError("Option sections must contain bullet points only")

        normalized = " ".join(normalized.split())
        if normalized:
            bullets.append(normalized)

    if len(bullets) < 2:
        raise ValueError("Each option must contain at least two bullet points")

    return bullets[:3]


def parse_answer_output(raw_text: str) -> ParsedAnswer:
    text = raw_text.strip()
    if not text:
        raise ValueError("Answer output is empty")

    option_a_block = _extract_option_block(text, "Option A", "Option B")
    option_b_block = _extract_option_block(text, "Option B", None)

    return ParsedAnswer(
        option_a=_parse_bullets(option_a_block),
        option_b=_parse_bullets(option_b_block),
    )
