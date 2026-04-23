import type { RealtimeSessionState } from '../state/realtime-session-store'

type Props = {
  state: RealtimeSessionState
  onReconnect: () => void
  onToggleVisible: () => void
}

const joinLines = (items: string[]) => (items.length ? items : ['Waiting for response...'])

export const FloatingOverlayPanel = ({ state, onReconnect, onToggleVisible }: Props) => {
  if (!state.overlayVisible) {
    return (
      <button className="overlay-reopen" onClick={onToggleVisible} type="button">
        Open Copilot
      </button>
    )
  }

  return (
    <section className="overlay-panel" aria-live="polite">
      <header className="overlay-header">
        <div>
          <strong>Interview Copilot</strong>
          <div className="overlay-subtitle">Transport: {state.transport}</div>
        </div>
        <div className="overlay-controls">
          <button type="button" onClick={onReconnect}>
            Reconnect
          </button>
          <button type="button" onClick={onToggleVisible}>
            Close
          </button>
        </div>
      </header>

      <div className="overlay-status">State: {state.agentState}</div>
      <div className="overlay-message">{state.statusMessage}</div>

      {state.errorMessage ? <div className="overlay-error">{state.errorMessage}</div> : null}

      <div className="overlay-block">
        <div className="overlay-label">Question</div>
        <div className="overlay-content">{state.finalQuestion || state.partialTranscript || 'Listening...'}</div>
      </div>

      <div className="overlay-block">
        <div className="overlay-label">Option A</div>
        <ul>
          {joinLines(state.optionA).map((line) => (
            <li key={`a-${line}`}>{line}</li>
          ))}
        </ul>
      </div>

      <div className="overlay-block">
        <div className="overlay-label">Option B</div>
        <ul>
          {joinLines(state.optionB).map((line) => (
            <li key={`b-${line}`}>{line}</li>
          ))}
        </ul>
      </div>

      <footer className="overlay-footer">
        <span>Lang: {state.answerLanguage}</span>
        <span>Type: {state.questionType || 'n/a'}</span>
        <span>QC: {state.qcStatus}</span>
      </footer>
    </section>
  )
}
