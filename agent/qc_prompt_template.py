from __future__ import annotations


def _target_language(language: str) -> str:
    return "Vietnamese" if language.strip().lower() == "vi" else "English"


def build_qc_prompt(
    source_text: str,
    language: str,
    question_type: str,
    keywords: list[str],
) -> str:
    normalized_text = " ".join(source_text.strip().split())
    keyword_text = ", ".join(keywords) if keywords else "none"
    target_language = _target_language(language)

    return (
        "You are an interview copilot. Produce concise, interview-ready answer options.\n"
        f"Question: {normalized_text}\n"
        f"Question Type: {question_type}\n"
        f"Keywords: {keyword_text}\n"
        f"Output Language: {target_language}\n\n"
        "Output rules:\n"
        "- Respond using only the requested output language.\n"
        "- Use exactly two sections: Option A and Option B.\n"
        "- Each section must contain 2-3 bullet points.\n"
        "- Keep each bullet short and practical for interview delivery.\n"
        "- Do not include introductions, conclusions, or extra headings.\n\n"
        "Return this exact structure:\n"
        "Option A:\n"
        "- ...\n"
        "- ...\n"
        "Option B:\n"
        "- ...\n"
        "- ..."
    )
