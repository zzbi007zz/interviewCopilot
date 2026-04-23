import { describe, expect, it } from 'vitest'

import { EVENT_TYPES, PROTOCOL_VERSION } from '../lib/protocol'
import { initialRealtimeSessionState, reduceRealtimeSessionEvent } from '../state/realtime-session-store'

describe('realtime-session-store', () => {
  it('updates question and answer fields from events', () => {
    const transcriptState = reduceRealtimeSessionEvent(initialRealtimeSessionState, {
      protocolVersion: PROTOCOL_VERSION,
      type: EVENT_TYPES.TRANSCRIPT_FINAL,
      timestamp: new Date().toISOString(),
      sessionId: 'session-1',
      payload: {
        text: 'Explain POM pattern',
        language: 'en',
        confidence: 0.98,
      },
    })

    const answerState = reduceRealtimeSessionEvent(transcriptState, {
      protocolVersion: PROTOCOL_VERSION,
      type: EVENT_TYPES.ANSWER_GENERATED,
      timestamp: new Date().toISOString(),
      sessionId: 'session-1',
      payload: {
        sourceText: 'Explain POM pattern',
        questionType: 'conceptual',
        optionA: ['A1', 'A2'],
        optionB: ['B1', 'B2'],
        language: 'en',
        fallbackUsed: false,
        qcStatus: 'passed',
      },
    })

    expect(answerState.finalQuestion).toBe('Explain POM pattern')
    expect(answerState.optionA).toEqual(['A1', 'A2'])
    expect(answerState.optionB).toEqual(['B1', 'B2'])
    expect(answerState.answerLanguage).toBe('en')
  })

  it('drops stale answer events for previous question', () => {
    const currentState = {
      ...initialRealtimeSessionState,
      finalQuestion: 'Question B',
      optionA: ['B-current'],
      optionB: ['B-current-2'],
    }

    const staleAnswerState = reduceRealtimeSessionEvent(currentState, {
      protocolVersion: PROTOCOL_VERSION,
      type: EVENT_TYPES.ANSWER_GENERATED,
      timestamp: new Date().toISOString(),
      sessionId: 'session-1',
      payload: {
        sourceText: 'Question A',
        questionType: 'conceptual',
        optionA: ['A-old-1', 'A-old-2'],
        optionB: ['A-old-3', 'A-old-4'],
        language: 'en',
        fallbackUsed: false,
        qcStatus: 'passed',
      },
    })

    expect(staleAnswerState.finalQuestion).toBe('Question B')
    expect(staleAnswerState.optionA).toEqual(['B-current'])
    expect(staleAnswerState.optionB).toEqual(['B-current-2'])
  })

  it('tracks health diagnostics snapshot data', () => {
    const nextState = reduceRealtimeSessionEvent(initialRealtimeSessionState, {
      protocolVersion: PROTOCOL_VERSION,
      type: EVENT_TYPES.HEALTH_DIAGNOSTICS,
      timestamp: new Date().toISOString(),
      sessionId: 'session-1',
      payload: {
        sessionId: 'session-1',
        startedAt: new Date().toISOString(),
        state: 'processing',
        audioReady: true,
        provider: 'local-fallback',
        fallbackActive: true,
        counts: {
          partialTranscripts: 2,
          finalTranscripts: 1,
          answers: 1,
          errors: 1,
        },
        lastEvents: {
          partialAt: new Date().toISOString(),
          finalAt: new Date().toISOString(),
          answerAt: new Date().toISOString(),
        },
        lastError: {
          code: 'ASR_PRIMARY_TIMEOUT',
          stage: 'asr-primary',
          retryable: true,
        },
        message: 'fallback-activated',
      },
    })

    expect(nextState.agentState).toBe('processing')
    expect(nextState.healthMessage).toBe('fallback-activated')
    expect(nextState.diagnostics.provider).toBe('local-fallback')
    expect(nextState.diagnostics.fallbackActive).toBe(true)
    expect(nextState.diagnostics.audioReady).toBe(true)
    expect(nextState.diagnostics.partialTranscripts).toBe(2)
    expect(nextState.diagnostics.finalTranscripts).toBe(1)
    expect(nextState.diagnostics.answers).toBe(1)
    expect(nextState.diagnostics.errors).toBe(1)
    expect(nextState.diagnostics.lastErrorCode).toBe('ASR_PRIMARY_TIMEOUT')
    expect(nextState.diagnostics.lastErrorStage).toBe('asr-primary')
  })
})
