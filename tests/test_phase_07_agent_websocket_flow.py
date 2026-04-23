import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agent')))

from asr_provider import ASRResult
from config import AgentConfig
from message_router import route_asr_result
from runtime_state import RuntimeState


class RecordingHub:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict, dict | None]] = []

    async def broadcast(self, event_type: str, payload: dict, metadata: dict | None = None) -> None:
        self.events.append((event_type, payload, metadata))


class Phase07AgentWebSocketFlowTest(unittest.TestCase):
    def _run_route(self, result: ASRResult, hub: RecordingHub, state: RuntimeState, config: AgentConfig) -> None:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(route_asr_result(result, hub, state, config))
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    def _base_config(self) -> AgentConfig:
        return AgentConfig(
            deepgram_key=None,
            anthropic_key=None,
            whisper_api_key=None,
            translation_api_key=None,
            ws_host='127.0.0.1',
            ws_port=8765,
            default_language='auto',
            zero_storage_mode=True,
            audio_device_name='BlackHole',
            audio_sample_rate=16000,
            audio_chunk_ms=250,
            asr_primary_provider='deepgram',
            asr_fallback_enabled=True,
            asr_primary_timeout_ms=3000,
            language_detection_enabled=True,
            translation_enabled=False,
            intent_llm_assist_enabled=False,
            answer_max_tokens=200,
            answer_provider_timeout_ms=2500,
        )

    def test_final_transcript_routes_transcript_intent_answer_in_order(self) -> None:
        hub = RecordingHub()
        state = RuntimeState()
        config = self._base_config()

        final_result = ASRResult(
            kind='final',
            text='Explain page object model',
            language='en',
            confidence=0.98,
        )

        self._run_route(final_result, hub, state, config)

        self.assertEqual(len(hub.events), 3)

        event_types = [event_type for event_type, _, _ in hub.events]
        self.assertEqual(
            event_types,
            ['transcript.final', 'intent.detected', 'answer.generated'],
        )

        transcript_payload = hub.events[0][1]
        transcript_metadata = hub.events[0][2]
        self.assertEqual(transcript_payload['text'], 'Explain page object model')
        self.assertEqual(transcript_payload['language'], 'en')
        self.assertEqual(transcript_payload['confidence'], 0.98)
        self.assertIsNotNone(transcript_metadata)
        self.assertEqual(transcript_metadata['provider'], 'deepgram-primary')
        self.assertEqual(transcript_metadata['fallbackActive'], False)
        self.assertEqual(transcript_metadata['audioReady'], False)
        self.assertEqual(transcript_metadata['zeroStorageMode'], True)

        intent_payload = hub.events[1][1]
        intent_metadata = hub.events[1][2]
        self.assertEqual(intent_payload['questionType'], 'conceptual')
        self.assertIn('page object model', intent_payload['keywords'])
        self.assertEqual(intent_metadata, transcript_metadata)

        answer_payload = hub.events[2][1]
        answer_metadata = hub.events[2][2]
        self.assertEqual(answer_payload['sourceText'], 'Explain page object model')
        self.assertEqual(answer_payload['questionType'], 'conceptual')
        self.assertIn(answer_payload['language'], ('en', 'vi'))
        self.assertIsInstance(answer_payload['fallbackUsed'], bool)
        self.assertIn(answer_payload['qcStatus'], ('passed', 'fallback'))
        self.assertGreaterEqual(len(answer_payload['optionA']), 2)
        self.assertGreaterEqual(len(answer_payload['optionB']), 2)
        self.assertEqual(answer_metadata, transcript_metadata)

    def test_duplicate_final_transcript_is_suppressed(self) -> None:
        hub = RecordingHub()
        state = RuntimeState()
        config = self._base_config()

        final_result = ASRResult(
            kind='final',
            text='Explain page object model',
            language='en',
            confidence=0.98,
        )

        self._run_route(final_result, hub, state, config)
        first_event_count = len(hub.events)
        self._run_route(final_result, hub, state, config)

        self.assertEqual(first_event_count, 3)
        self.assertEqual(len(hub.events), 3)

    def test_error_event_uses_explicit_taxonomy_and_stage(self) -> None:
        hub = RecordingHub()
        state = RuntimeState()
        config = self._base_config()

        error_result = ASRResult(
            kind='error',
            text='',
            error_code='ASR_PRIMARY_TIMEOUT',
            error_stage='asr-primary',
        )

        self._run_route(error_result, hub, state, config)

        self.assertEqual(len(hub.events), 1)
        event_type, payload, metadata = hub.events[0]
        self.assertEqual(event_type, 'error')
        self.assertEqual(payload['code'], 'ASR_PRIMARY_TIMEOUT')
        self.assertEqual(payload['message'], 'Primary ASR timed out')
        self.assertEqual(payload['retryable'], True)
        self.assertEqual(payload['stage'], 'asr-primary')
        self.assertEqual(metadata['provider'], 'deepgram-primary')
        self.assertEqual(state.last_error_code, 'ASR_PRIMARY_TIMEOUT')
        self.assertEqual(state.last_error_stage, 'asr-primary')
        self.assertEqual(state.error_count, 1)


if __name__ == '__main__':
    unittest.main()
