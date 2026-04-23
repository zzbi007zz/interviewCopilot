import { useCallback } from 'react'
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { useLocalAgentWebSocket } from '../hooks/use-local-agent-websocket'

class MockWebSocket {
  static instances: MockWebSocket[] = []

  onopen: (() => void) | null = null
  onclose: (() => void) | null = null
  onerror: (() => void) | null = null
  onmessage: ((event: { data: string }) => void) | null = null

  constructor(readonly url: string) {
    MockWebSocket.instances.push(this)
  }

  close() {
    this.onclose?.()
  }
}

const HookHarness = () => {
  const onEvent = useCallback(() => undefined, [])
  const onError = useCallback(() => undefined, [])
  const { transport, reconnect, disconnect } = useLocalAgentWebSocket({
    onEvent,
    onError,
  })

  return (
    <>
      <div data-testid="transport">{transport}</div>
      <button type="button" onClick={reconnect}>
        reconnect
      </button>
      <button type="button" onClick={disconnect}>
        disconnect
      </button>
    </>
  )
}

describe('use-local-agent-websocket', () => {
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
    MockWebSocket.instances = []
  })

  it('reconnects after abnormal close and skips reconnect after manual disconnect', () => {
    vi.useFakeTimers()
    MockWebSocket.instances = []
    vi.stubGlobal('WebSocket', MockWebSocket as unknown as typeof WebSocket)

    render(<HookHarness />)

    expect(MockWebSocket.instances.length).toBe(1)
    act(() => {
      MockWebSocket.instances[0].onopen?.()
    })
    expect(screen.getByTestId('transport').textContent).toBe('connected')

    expect(typeof MockWebSocket.instances[0].onclose).toBe('function')
    act(() => {
      MockWebSocket.instances[0].close()
    })
    expect(screen.getByTestId('transport').textContent).toBe('reconnecting')

    act(() => {
      vi.advanceTimersByTime(250)
    })
    expect(MockWebSocket.instances.length).toBe(2)

    act(() => {
      MockWebSocket.instances[1].onopen?.()
    })
    expect(screen.getByTestId('transport').textContent).toBe('connected')

    fireEvent.click(screen.getByText('disconnect'))
    expect(screen.getByTestId('transport').textContent).toBe('disconnected')

    act(() => {
      vi.advanceTimersByTime(5000)
    })
    expect(MockWebSocket.instances.length).toBe(2)

  })
})
