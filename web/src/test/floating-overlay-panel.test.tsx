import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { FloatingOverlayPanel } from '../components/floating-overlay-panel'
import { initialRealtimeSessionState } from '../state/realtime-session-store'

describe('floating-overlay-panel', () => {
  it('renders status and answer options as plain text', () => {
    const state = {
      ...initialRealtimeSessionState,
      transport: 'connected' as const,
      agentState: 'responding' as const,
      finalQuestion: 'Explain Selenium retries',
      optionA: ['Use explicit retry policy'],
      optionB: ['Use flaky-test quarantine'],
    }

    render(
      <FloatingOverlayPanel state={state} onReconnect={() => undefined} onToggleVisible={() => undefined} />,
    )

    expect(screen.getByText('Interview Copilot')).toBeTruthy()
    expect(screen.getByText('Explain Selenium retries')).toBeTruthy()
    expect(screen.getByText('Use explicit retry policy')).toBeTruthy()
    expect(screen.getByText('Use flaky-test quarantine')).toBeTruthy()
  })
})
