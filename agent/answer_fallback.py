from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FallbackAnswer:
    option_a: list[str]
    option_b: list[str]
    language: str


def _english_templates(question_type: str) -> tuple[list[str], list[str]]:
    if question_type == "debugging":
        return (
            [
                "State the issue clearly, then explain the first check you run.",
                "Describe root-cause validation before applying a fix.",
            ],
            [
                "Walk through logs, reproduction, and isolation step-by-step.",
                "End with prevention actions such as tests or alerts.",
            ],
        )

    if question_type == "qa-automation":
        return (
            [
                "Explain coverage strategy across smoke, regression, and edge cases.",
                "Mention stable selectors and maintainable test design.",
            ],
            [
                "Describe CI integration and failure triage workflow.",
                "Highlight how flaky tests are detected and controlled.",
            ],
        )

    return (
        [
            "Start with a short definition, then connect it to practical impact.",
            "Give one concrete example from a recent project.",
        ],
        [
            "Compare with an alternative approach and when to choose each.",
            "Close with a concise recommendation tied to results.",
        ],
    )


def _vietnamese_templates(question_type: str) -> tuple[list[str], list[str]]:
    if question_type == "debugging":
        return (
            [
                "Nêu rõ lỗi, sau đó trình bày bước kiểm tra đầu tiên.",
                "Xác minh nguyên nhân gốc trước khi sửa.",
            ],
            [
                "Mô tả quy trình tái hiện lỗi và cô lập phạm vi ảnh hưởng.",
                "Kết thúc bằng biện pháp phòng ngừa như test và giám sát.",
            ],
        )

    if question_type == "qa-automation":
        return (
            [
                "Giải thích chiến lược bao phủ test: smoke, regression, edge case.",
                "Nêu cách thiết kế test dễ bảo trì và selector ổn định.",
            ],
            [
                "Trình bày cách tích hợp CI và xử lý test fail.",
                "Đề cập cách kiểm soát flaky test trong pipeline.",
            ],
        )

    return (
        [
            "Bắt đầu bằng định nghĩa ngắn gọn và giá trị thực tế.",
            "Đưa một ví dụ cụ thể từ dự án gần đây.",
        ],
        [
            "So sánh với phương án khác và bối cảnh áp dụng.",
            "Chốt lại bằng khuyến nghị ngắn, tập trung vào kết quả.",
        ],
    )


def generate_fallback_answer(language: str, question_type: str) -> FallbackAnswer:
    normalized_language = "vi" if language.strip().lower() == "vi" else "en"

    if normalized_language == "vi":
        option_a, option_b = _vietnamese_templates(question_type)
    else:
        option_a, option_b = _english_templates(question_type)

    return FallbackAnswer(option_a=option_a, option_b=option_b, language=normalized_language)
