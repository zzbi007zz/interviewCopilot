import { useMemo, useState } from 'react'

import { FloatingOverlayPanel } from './components/floating-overlay-panel'
import { useLocalAgentWebSocket } from './hooks/use-local-agent-websocket'
import type { RealtimeEvent } from './lib/protocol'
import {
  initialRealtimeSessionState,
  reduceRealtimeSessionEvent,
  type RealtimeSessionState,
} from './state/realtime-session-store'

export const App = () => {
  const [state, setState] = useState<RealtimeSessionState>(initialRealtimeSessionState)

  const handleEvent = useMemo(
    () => (event: RealtimeEvent) => {
      setState((current) => reduceRealtimeSessionEvent(current, event))
    },
    [],
  )

  const handleError = useMemo(
    () => (message: string) => {
      setState((current) => ({
        ...current,
        errorMessage: message,
        statusMessage: message || current.statusMessage,
      }))
    },
    [],
  )

  const { transport, reconnect } = useLocalAgentWebSocket({
    onEvent: handleEvent,
    onError: handleError,
  })

  const toggleOverlay = () => {
    setState((current) => ({ ...current, overlayVisible: !current.overlayVisible }))
  }

  return (
    <FloatingOverlayPanel
      state={{ ...state, transport }}
      onReconnect={reconnect}
      onToggleVisible={toggleOverlay}
    />
  )
}
