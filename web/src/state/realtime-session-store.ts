import { EVENT_TYPES, type RealtimeEvent } from '../lib/protocol'

export type TransportStatus = 'idle' | 'connecting' | 'connected' | 'reconnecting' | 'disconnected'

export type RealtimeSessionState = {
  transport: TransportStatus
  agentState: 'idle' | 'listening' | 'processing' | 'responding' | 'error'
  statusMessage: string
  partialTranscript: string
  finalQuestion: string
  questionType: string
  detectedLanguage: string
  answerLanguage: 'en' | 'vi'
  optionA: string[]
  optionB: string[]
  fallbackUsed: boolean
  qcStatus: 'passed' | 'fallback'
  errorMessage: string
  healthMessage: string
  diagnostics: {
    provider: string
    fallbackActive: boolean
    audioReady: boolean
    partialTranscripts: number
    finalTranscripts: number
    answers: number
    errors: number
    lastErrorCode: string
    lastErrorStage: string
  }
  overlayVisible: boolean
}

export const initialRealtimeSessionState: RealtimeSessionState = {
  transport: 'idle',
  agentState: 'idle',
  statusMessage: 'Waiting for local agent',
  partialTranscript: '',
  finalQuestion: '',
  questionType: '',
  detectedLanguage: 'en',
  answerLanguage: 'en',
  optionA: [],
  optionB: [],
  fallbackUsed: false,
  qcStatus: 'passed',
  errorMessage: '',
  healthMessage: '',
  diagnostics: {
    provider: '',
    fallbackActive: false,
    audioReady: false,
    partialTranscripts: 0,
    finalTranscripts: 0,
    answers: 0,
    errors: 0,
    lastErrorCode: '',
    lastErrorStage: '',
  },
  overlayVisible: true,
}

export const reduceRealtimeSessionEvent = (
  state: RealtimeSessionState,
  event: RealtimeEvent,
): RealtimeSessionState => {
  switch (event.type) {
    case EVENT_TYPES.STATUS_UPDATE:
      return {
        ...state,
        agentState: event.payload.state,
        statusMessage: event.payload.message || state.statusMessage,
        errorMessage: event.payload.state === 'error' ? state.errorMessage : '',
      }
    case EVENT_TYPES.TRANSCRIPT_PARTIAL:
      return {
        ...state,
        partialTranscript: event.payload.text,
        detectedLanguage: event.payload.language || state.detectedLanguage,
      }
    case EVENT_TYPES.TRANSCRIPT_FINAL:
      return {
        ...state,
        finalQuestion: event.payload.text,
        partialTranscript: '',
        detectedLanguage: event.payload.language || state.detectedLanguage,
      }
    case EVENT_TYPES.INTENT_DETECTED:
      return {
        ...state,
        questionType: event.payload.questionType,
        detectedLanguage: event.payload.language || state.detectedLanguage,
      }
    case EVENT_TYPES.ANSWER_GENERATED:
      if (state.finalQuestion && state.finalQuestion !== event.payload.sourceText) {
        return state
      }

      return {
        ...state,
        finalQuestion: event.payload.sourceText,
        questionType: event.payload.questionType,
        optionA: event.payload.optionA,
        optionB: event.payload.optionB,
        answerLanguage: event.payload.language,
        fallbackUsed: event.payload.fallbackUsed,
        qcStatus: event.payload.qcStatus,
        errorMessage: '',
      }
    case EVENT_TYPES.HEALTH_DIAGNOSTICS:
      return {
        ...state,
        agentState: event.payload.state,
        healthMessage: event.payload.message || state.healthMessage,
        diagnostics: {
          provider: event.payload.provider,
          fallbackActive: event.payload.fallbackActive,
          audioReady: event.payload.audioReady,
          partialTranscripts: event.payload.counts.partialTranscripts,
          finalTranscripts: event.payload.counts.finalTranscripts,
          answers: event.payload.counts.answers,
          errors: event.payload.counts.errors,
          lastErrorCode: event.payload.lastError.code || '',
          lastErrorStage: event.payload.lastError.stage || '',
        },
      }
    case EVENT_TYPES.ERROR:
      return {
        ...state,
        errorMessage: event.payload.message,
        statusMessage: event.payload.message,
      }
    default:
      return state
  }
}
