import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { createRealtimeMessageHandler, type RealtimeEvent } from '../lib/protocol'
import { buildLocalAgentWebSocketUrl } from '../lib/local-agent-url'

type HookConfig = {
  host?: string
  port?: number
  onEvent: (event: RealtimeEvent) => void
  onError: (message: string) => void
}

const RETRY_DELAYS_MS = [250, 500, 1000, 2000, 4000]

export const useLocalAgentWebSocket = ({
  host = '127.0.0.1',
  port = 8765,
  onEvent,
  onError,
}: HookConfig) => {
  const [transport, setTransport] = useState<'idle' | 'connecting' | 'connected' | 'reconnecting' | 'disconnected'>(
    'idle',
  )
  const retryIndexRef = useRef(0)
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<number | null>(null)
  const manualCloseRef = useRef(false)

  const wsUrl = useMemo(() => buildLocalAgentWebSocketUrl(port, host), [port, host])

  const clearTimer = useCallback(() => {
    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current)
      reconnectTimerRef.current = null
    }
  }, [])

  const closeSocket = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close()
      socketRef.current = null
    }
  }, [])

  const scheduleReconnect = useCallback(
    (connect: () => void) => {
      const delay = RETRY_DELAYS_MS[Math.min(retryIndexRef.current, RETRY_DELAYS_MS.length - 1)]
      retryIndexRef.current += 1
      setTransport('reconnecting')
      reconnectTimerRef.current = window.setTimeout(connect, delay)
    },
    [setTransport],
  )

  const connect = useCallback(() => {
    clearTimer()
    closeSocket()
    setTransport((current) => (current === 'idle' ? 'connecting' : current))

    const socket = new WebSocket(wsUrl)
    socketRef.current = socket

    const handleMessage = createRealtimeMessageHandler(onEvent, (message) => onError(message))

    socket.onopen = () => {
      retryIndexRef.current = 0
      setTransport('connected')
      onError('')
    }

    socket.onmessage = (event) => {
      if (typeof event.data === 'string') {
        handleMessage(event.data)
      }
    }

    socket.onerror = () => {
      onError('WebSocket connection error')
    }

    socket.onclose = () => {
      if (socketRef.current === socket) {
        socketRef.current = null
      }
      if (manualCloseRef.current) {
        setTransport('disconnected')
        return
      }
      scheduleReconnect(connect)
    }
  }, [clearTimer, closeSocket, onError, onEvent, scheduleReconnect, wsUrl])

  const reconnect = useCallback(() => {
    manualCloseRef.current = false
    retryIndexRef.current = 0
    setTransport('connecting')
    connect()
  }, [connect])

  const disconnect = useCallback(() => {
    manualCloseRef.current = true
    clearTimer()
    closeSocket()
    setTransport('disconnected')
  }, [clearTimer, closeSocket])

  useEffect(() => {
    reconnect()
    return () => {
      manualCloseRef.current = true
      clearTimer()
      closeSocket()
    }
  }, [clearTimer, closeSocket, reconnect])

  return { transport, reconnect, disconnect }
}
