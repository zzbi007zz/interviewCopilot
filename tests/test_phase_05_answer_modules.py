import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agent")))

from answer_orchestrator import generate_answer_payload
from answer_output_parser import parse_answer_output
from config import AgentConfig
from language_and_intent_pipeline import PipelineOutput


class Phase05AnswerModulesTest(unittest.TestCase):
    def _base_config(self) -> AgentConfig:
        return AgentConfig(
            deepgram_key=None,
            anthropic_key=None,
            whisper_api_key=None,
            translation_api_key=None,
            ws_host="127.0.0.1",
            ws_port=8765,
            default_language="auto",
            zero_storage_mode=True,
            audio_device_name="BlackHole",
            audio_sample_rate=16000,
            audio_chunk_ms=250,
            asr_primary_provider="deepgram",
            asr_fallback_enabled=True,
            asr_primary_timeout_ms=3000,
            language_detection_enabled=True,
            translation_enabled=False,
            intent_llm_assist_enabled=False,
            answer_max_tokens=200,
            answer_provider_timeout_ms=2500,
        )

    def test_parser_rejects_non_bullet_prose(self) -> None:
        malformed = """Option A:
This line should be rejected
- Bullet one
Option B:
- Bullet two
- Bullet three
"""
        with self.assertRaises(ValueError):
            parse_answer_output(malformed)

    def test_parser_rejects_mixed_prose_with_enough_bullets(self) -> None:
        malformed = """Option A:
- Bullet one
This prose line should fail
- Bullet two
Option B:
- Bullet three
- Bullet four
"""
        with self.assertRaises(ValueError):
            parse_answer_output(malformed)

    def test_orchestrator_normalizes_auto_language_to_en(self) -> None:
        config = self._base_config()
        pipeline = PipelineOutput(
            normalized_text="Explain page object model",
            language="auto",
            question_type="conceptual",
            keywords=["page object model"],
        )

        payload = asyncio.run(
            generate_answer_payload(
                source_text="Explain page object model",
                pipeline=pipeline,
                config=config,
            )
        )

        self.assertEqual(payload.language, "en")
        self.assertTrue(payload.fallback_used)
        self.assertEqual(payload.qc_status, "fallback")
        self.assertGreaterEqual(len(payload.option_a), 2)
        self.assertGreaterEqual(len(payload.option_b), 2)


if __name__ == "__main__":
    unittest.main()
