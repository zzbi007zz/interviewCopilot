import {
  EVENT_TYPES,
  PROTOCOL_VERSION,
  assertRealtimeEvent,
  assertRealtimeEventEnvelope,
  isRealtimeEvent,
  isRealtimeEventEnvelope,
  type RealtimeEvent,
  type RealtimeEventEnvelope,
} from '../../../shared/realtime-event-contracts'

export {
  EVENT_TYPES,
  PROTOCOL_VERSION,
  type RealtimeEvent,
  type RealtimeEventEnvelope,
  isRealtimeEvent,
  isRealtimeEventEnvelope,
}

type RealtimeParseErrorCode = 'INVALID_JSON' | 'INVALID_PAYLOAD'
type WebSocketMessageHandler = (event: RealtimeEvent) => void
type WebSocketErrorHandler = (message: string, code: RealtimeParseErrorCode) => void

const parseRealtimePayload = (payload: unknown): RealtimeEvent[] => {
  if (isRealtimeEvent(payload)) {
    return [payload]
  }

  if (isRealtimeEventEnvelope(payload)) {
    return payload.events
  }

  throw new Error('INVALID_PAYLOAD')
}

export const parseRealtimeMessage = (rawMessage: string): RealtimeEvent => {
  const parsed = JSON.parse(rawMessage)
  return assertRealtimeEvent(parsed)
}

export const parseRealtimeEnvelope = (rawMessage: string): RealtimeEventEnvelope => {
  const parsed = JSON.parse(rawMessage)
  return assertRealtimeEventEnvelope(parsed)
}

export const parseRealtimeMessages = (rawMessage: string): RealtimeEvent[] => {
  let parsed: unknown

  try {
    parsed = JSON.parse(rawMessage)
  } catch {
    throw new Error('INVALID_JSON')
  }

  return parseRealtimePayload(parsed)
}

export const createRealtimeMessageHandler =
  (onEvent: WebSocketMessageHandler, onError?: WebSocketErrorHandler) =>
  (rawMessage: string): void => {
    let events: RealtimeEvent[]

    try {
      events = parseRealtimeMessages(rawMessage)
    } catch (error) {
      if (!onError) return

      const code: RealtimeParseErrorCode =
        error instanceof Error && error.message === 'INVALID_JSON'
          ? 'INVALID_JSON'
          : 'INVALID_PAYLOAD'

      const message =
        code === 'INVALID_JSON'
          ? 'Invalid realtime message format'
          : 'Unsupported realtime payload shape'

      onError(message, code)
      return
    }

    for (const event of events) {
      onEvent(event)
    }
  }
