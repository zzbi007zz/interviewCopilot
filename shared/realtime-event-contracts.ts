export const PROTOCOL_VERSION = '1.0.0' as const

export const EVENT_TYPES = {
  TRANSCRIPT_PARTIAL: 'transcript.partial',
  TRANSCRIPT_FINAL: 'transcript.final',
  INTENT_DETECTED: 'intent.detected',
  ANSWER_GENERATED: 'answer.generated',
  STATUS_UPDATE: 'status.update',
  HEALTH_DIAGNOSTICS: 'health.diagnostics',
  ERROR: 'error',
} as const

const STATUS_STATES = ['idle', 'listening', 'processing', 'responding', 'error'] as const

export type EventType = (typeof EVENT_TYPES)[keyof typeof EVENT_TYPES]

type Metadata = Record<string, string | number | boolean | null>

type BaseEvent = {
  protocolVersion: typeof PROTOCOL_VERSION
  type: EventType
  timestamp: string
  sessionId: string
  metadata?: Metadata
}

export type TranscriptPartialEvent = BaseEvent & {
  type: typeof EVENT_TYPES.TRANSCRIPT_PARTIAL
  payload: {
    text: string
    language?: string
  }
}

export type TranscriptFinalEvent = BaseEvent & {
  type: typeof EVENT_TYPES.TRANSCRIPT_FINAL
  payload: {
    text: string
    language?: string
    confidence?: number
  }
}

export type IntentDetectedEvent = BaseEvent & {
  type: typeof EVENT_TYPES.INTENT_DETECTED
  payload: {
    questionType: string
    keywords: string[]
    language?: string
  }
}

export type AnswerGeneratedEvent = BaseEvent & {
  type: typeof EVENT_TYPES.ANSWER_GENERATED
  payload: {
    sourceText: string
    questionType: string
    optionA: string[]
    optionB: string[]
    language: 'en' | 'vi'
    fallbackUsed: boolean
    qcStatus: 'passed' | 'fallback'
  }
}

export type StatusUpdateEvent = BaseEvent & {
  type: typeof EVENT_TYPES.STATUS_UPDATE
  payload: {
    state: (typeof STATUS_STATES)[number]
    message?: string
  }
}

export type HealthDiagnosticsEvent = BaseEvent & {
  type: typeof EVENT_TYPES.HEALTH_DIAGNOSTICS
  payload: {
    sessionId: string
    startedAt: string
    state: (typeof STATUS_STATES)[number]
    audioReady: boolean
    provider: string
    fallbackActive: boolean
    counts: {
      partialTranscripts: number
      finalTranscripts: number
      answers: number
      errors: number
    }
    lastEvents: {
      partialAt: string | null
      finalAt: string | null
      answerAt: string | null
    }
    lastError: {
      code: string | null
      stage: string | null
      retryable: boolean
    }
    message?: string
  }
}

export type ErrorEvent = BaseEvent & {
  type: typeof EVENT_TYPES.ERROR
  payload: {
    code: string
    message: string
    retryable: boolean
    stage?: string
  }
}

export type RealtimeEvent =
  | TranscriptPartialEvent
  | TranscriptFinalEvent
  | IntentDetectedEvent
  | AnswerGeneratedEvent
  | StatusUpdateEvent
  | HealthDiagnosticsEvent
  | ErrorEvent

export type RealtimeEventEnvelope = {
  protocolVersion: typeof PROTOCOL_VERSION
  events: RealtimeEvent[]
}

export const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

const EVENT_VALUES = Object.values(EVENT_TYPES)
const SENSITIVE_ERROR_PATTERN = /(api[_-]?key|secret|authorization|bearer|sk-[a-z0-9]{10,})/i
const STACK_LEAK_PATTERN = /(traceback|file\s+".*",\s+line\s+\d+|\sat\s+\S+\s+\()/i

const isStringArray = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) => typeof item === 'string')

const ANSWER_QC_STATUS_VALUES = ['passed', 'fallback'] as const
const ANSWER_LANGUAGE_VALUES = ['en', 'vi'] as const

const isOptionalString = (value: unknown): boolean => value === undefined || typeof value === 'string'
const isNullableString = (value: unknown): boolean => value === null || typeof value === 'string'

const isIsoTimestamp = (value: unknown): value is string =>
  typeof value === 'string' && !Number.isNaN(Date.parse(value))

const isMetadata = (value: unknown): value is Metadata => {
  if (value === undefined) return true
  if (!isRecord(value)) return false

  return Object.entries(value).every(([key, item]) => {
    if (SENSITIVE_ERROR_PATTERN.test(key)) return false

    if (item === null || typeof item === 'number' || typeof item === 'boolean') {
      return true
    }

    if (typeof item === 'string') {
      if (SENSITIVE_ERROR_PATTERN.test(item)) return false
      if (STACK_LEAK_PATTERN.test(item)) return false
      return true
    }

    return false
  })
}

const isSafeErrorMessage = (value: unknown): value is string => {
  if (typeof value !== 'string') return false
  if (!value.trim()) return false
  if (SENSITIVE_ERROR_PATTERN.test(value)) return false
  if (STACK_LEAK_PATTERN.test(value)) return false
  return true
}

type RealtimeEventCandidate = BaseEvent & { payload: Record<string, unknown> }

const hasBaseShape = (value: unknown): value is RealtimeEventCandidate => {
  if (!isRecord(value) || !isRecord(value.payload)) return false

  return (
    value.protocolVersion === PROTOCOL_VERSION &&
    typeof value.type === 'string' &&
    EVENT_VALUES.includes(value.type as EventType) &&
    isIsoTimestamp(value.timestamp) &&
    typeof value.sessionId === 'string' &&
    value.sessionId.trim().length > 0 &&
    isMetadata(value.metadata)
  )
}

export const isRealtimeEvent = (value: unknown): value is RealtimeEvent => {
  if (!hasBaseShape(value)) return false

  const payload = value.payload

  switch (value.type) {
    case EVENT_TYPES.TRANSCRIPT_PARTIAL:
      return typeof payload.text === 'string' && isOptionalString(payload.language)
    case EVENT_TYPES.TRANSCRIPT_FINAL:
      return (
        typeof payload.text === 'string' &&
        isOptionalString(payload.language) &&
        (payload.confidence === undefined || typeof payload.confidence === 'number')
      )
    case EVENT_TYPES.INTENT_DETECTED:
      return (
        typeof payload.questionType === 'string' &&
        isStringArray(payload.keywords) &&
        isOptionalString(payload.language)
      )
    case EVENT_TYPES.ANSWER_GENERATED:
      return (
        typeof payload.sourceText === 'string' &&
        typeof payload.questionType === 'string' &&
        isStringArray(payload.optionA) &&
        isStringArray(payload.optionB) &&
        typeof payload.language === 'string' &&
        ANSWER_LANGUAGE_VALUES.includes(
          payload.language as (typeof ANSWER_LANGUAGE_VALUES)[number],
        ) &&
        typeof payload.fallbackUsed === 'boolean' &&
        typeof payload.qcStatus === 'string' &&
        ANSWER_QC_STATUS_VALUES.includes(
          payload.qcStatus as (typeof ANSWER_QC_STATUS_VALUES)[number],
        )
      )
    case EVENT_TYPES.STATUS_UPDATE:
      return (
        typeof payload.state === 'string' &&
        STATUS_STATES.includes(payload.state as (typeof STATUS_STATES)[number]) &&
        isOptionalString(payload.message)
      )
    case EVENT_TYPES.HEALTH_DIAGNOSTICS:
      return (
        typeof payload.sessionId === 'string' &&
        isIsoTimestamp(payload.startedAt) &&
        typeof payload.state === 'string' &&
        STATUS_STATES.includes(payload.state as (typeof STATUS_STATES)[number]) &&
        typeof payload.audioReady === 'boolean' &&
        typeof payload.provider === 'string' &&
        typeof payload.fallbackActive === 'boolean' &&
        isRecord(payload.counts) &&
        typeof payload.counts.partialTranscripts === 'number' &&
        typeof payload.counts.finalTranscripts === 'number' &&
        typeof payload.counts.answers === 'number' &&
        typeof payload.counts.errors === 'number' &&
        isRecord(payload.lastEvents) &&
        isNullableString(payload.lastEvents.partialAt) &&
        isNullableString(payload.lastEvents.finalAt) &&
        isNullableString(payload.lastEvents.answerAt) &&
        isRecord(payload.lastError) &&
        isNullableString(payload.lastError.code) &&
        isNullableString(payload.lastError.stage) &&
        typeof payload.lastError.retryable === 'boolean' &&
        isOptionalString(payload.message)
      )
    case EVENT_TYPES.ERROR:
      return (
        typeof payload.code === 'string' &&
        isSafeErrorMessage(payload.message) &&
        typeof payload.retryable === 'boolean' &&
        (payload.stage === undefined || typeof payload.stage === 'string')
      )
    default:
      return false
  }
}

export const isRealtimeEventEnvelope = (value: unknown): value is RealtimeEventEnvelope => {
  if (!isRecord(value)) return false
  if (value.protocolVersion !== PROTOCOL_VERSION) return false
  if (!Array.isArray(value.events)) return false

  return value.events.every((event) => isRealtimeEvent(event))
}

export const assertRealtimeEvent = (value: unknown): RealtimeEvent => {
  if (!isRealtimeEvent(value)) {
    throw new Error('Invalid realtime event payload')
  }

  return value
}

export const assertRealtimeEventEnvelope = (value: unknown): RealtimeEventEnvelope => {
  if (!isRealtimeEventEnvelope(value)) {
    throw new Error('Invalid realtime event envelope')
  }

  return value
}
