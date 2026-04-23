# Phase 06 — Build web overlay UI realtime client

## Context Links
- Plan overview: `./plan.md`
- Depends on: `phase-02-define-shared-realtime-protocol-and-config-contracts.md`, `phase-03-build-local-agent-foundation-audio-and-websocket.md`, `phase-05-implement-answer-generation-and-qc-prompt-system.md`
- Contracts: `../../shared/realtime-event-contracts.ts`, `../../shared/config-contracts.md`
- Existing web adapter: `../../web/src/lib/protocol.ts`
- Agent websocket server: `../../agent/ws_hub.py`, `../../agent/main.py`

## Overview
- Priority: High
- Status: Completed
- Purpose: Build the smallest viable overlay that connects to the local agent websocket, renders current runtime state, and shows the latest interview question plus Option A/B answer suggestions.

## Key Insights
- Current web code only has protocol parsing in `web/src/lib/protocol.ts`; no app shell exists yet.
- Agent already enforces localhost peer/origin checks; web must not add any remote endpoint path around that protection.
- Protocol is already good enough for MVP UI: `status.update`, `transcript.partial`, `transcript.final`, `answer.generated`, `error`.
- YAGNI: Phase 06 should not add persistence, auth, history browser, markdown renderer, or multi-session UI.

## Requirements
- Functional:
  1. Connect to `ws://127.0.0.1:<port>` using local-only config.
  2. Render connection status separately from agent runtime status.
  3. Render latest status message, latest final question, latest partial transcript preview, Option A, Option B, and latest safe error.
  4. Provide only two controls: reconnect and close/hide overlay.
- Non-functional:
  1. Keep overlay compact, readable, and keyboard-safe.
  2. Keep all UI state in-memory only.
  3. Tolerate websocket restarts with bounded reconnect backoff.
  4. Preserve contract validation at websocket boundary.

## Minimal Architecture
- `web/src/lib/protocol.ts` — keep as single protocol parse boundary.
- `web/src/lib/local-agent-url.ts` — derive and validate localhost websocket URL.
- `web/src/state/realtime-session-store.ts` — pure reducer + initial state.
- `web/src/hooks/use-local-agent-websocket.ts` — socket lifecycle, reconnect, reducer dispatch.
- `web/src/components/floating-overlay-panel.tsx` — presentational overlay.
- `web/src/app.tsx` — composition root.
- `web/src/main.tsx` — React bootstrap.
- `web/src/styles/overlay.css` — compact overlay styling only.

## Exact Files To Create Or Modify

### Create
- `/Users/february10/Documents/interviewCopilot/web/package.json`
- `/Users/february10/Documents/interviewCopilot/web/tsconfig.json`
- `/Users/february10/Documents/interviewCopilot/web/vite.config.ts`
- `/Users/february10/Documents/interviewCopilot/web/index.html`
- `/Users/february10/Documents/interviewCopilot/web/src/main.tsx`
- `/Users/february10/Documents/interviewCopilot/web/src/app.tsx`
- `/Users/february10/Documents/interviewCopilot/web/src/components/floating-overlay-panel.tsx`
- `/Users/february10/Documents/interviewCopilot/web/src/hooks/use-local-agent-websocket.ts`
- `/Users/february10/Documents/interviewCopilot/web/src/state/realtime-session-store.ts`
- `/Users/february10/Documents/interviewCopilot/web/src/lib/local-agent-url.ts`
- `/Users/february10/Documents/interviewCopilot/web/src/styles/overlay.css`
- `/Users/february10/Documents/interviewCopilot/web/src/test/realtime-session-store.test.ts`
- `/Users/february10/Documents/interviewCopilot/web/src/test/use-local-agent-websocket.test.tsx`
- `/Users/february10/Documents/interviewCopilot/web/src/test/floating-overlay-panel.test.tsx`

### Modify
- `/Users/february10/Documents/interviewCopilot/web/src/lib/protocol.ts`
  - only if needed to export helper types used by hook/tests; no contract drift.

## State Model

```ts
type OverlayConnectionState = 'idle' | 'connecting' | 'connected' | 'reconnecting' | 'disconnected'

type OverlayViewState = {
  connectionState: OverlayConnectionState
  reconnectAttempt: number
  endpoint: string
  sessionId: string | null
  protocolVersion: string | null
  agentState: 'idle' | 'listening' | 'processing' | 'responding' | 'error'
  statusMessage: string
  partialTranscript: string
  finalQuestion: string
  detectedLanguage: string | null
  questionType: string | null
  optionA: string[]
  optionB: string[]
  answerLanguage: string | null
  fallbackUsed: boolean
  qcStatus: 'passed' | 'fallback' | null
  lastError: { code: string; message: string; retryable: boolean } | null
  overlayVisible: boolean
}
```

### Event → state flow
1. `status.update`
   - input: agent state + optional message
   - transform: update `agentState`, `statusMessage`, `sessionId`, `protocolVersion`
   - output: status banner text + badge color
2. `transcript.partial`
   - input: partial text
   - transform: overwrite `partialTranscript`
   - output: muted "hearing now" line only
3. `transcript.final`
   - input: finalized question text
   - transform: set `finalQuestion`, clear `partialTranscript`, update `detectedLanguage`
   - output: primary question block
4. `intent.detected`
   - input: question type + language
   - transform: set `questionType`, update language if present
   - output: small metadata row only
5. `answer.generated`
   - input: option arrays, qc flags
   - transform: replace answer block atomically
   - output: Option A / Option B lists
6. `error`
   - input: safe code/message/retryable
   - transform: set `lastError`, force `agentState='error'` only if current agent state is not fresher than a later status event
   - output: inline non-HTML error banner
7. socket close/open events
   - input: browser websocket lifecycle
   - transform: update `connectionState`, `reconnectAttempt`, `statusMessage`
   - output: transport status chip + reconnect affordance

## Minimal Implementation Steps
1. Add minimal web runtime scaffold with Vite + React + TypeScript only. No Tailwind in Phase 06; plain CSS is enough and lower risk.
2. Add `local-agent-url.ts` to build `ws://127.0.0.1:8765` by default and reject non-local hosts (`localhost`, `127.0.0.1` only).
3. Add pure reducer store in `realtime-session-store.ts` with typed actions mapped 1:1 to protocol events and websocket lifecycle events.
4. Add `use-local-agent-websocket.ts`:
   - create socket on mount when overlay visible
   - parse each inbound message through `createRealtimeMessageHandler`
   - dispatch reducer actions only after payload validation passes
   - reconnect on abnormal close with capped backoff
   - expose `reconnectNow()` and `disconnect()`
5. Add `floating-overlay-panel.tsx` as dumb UI:
   - top row: connection chip, agent chip, reconnect, close
   - middle: latest question + partial transcript preview
   - bottom: Option A and Option B bullet lists
   - error strip text-only
6. Add `app.tsx` to host one overlay instance and keep Phase 06 scope single-screen.
7. Add CSS for fixed floating panel approx `320x200` baseline, scroll inside answer area, safe text wrapping, no HTML injection surfaces.
8. Add tests for reducer transitions, websocket reconnect scheduling, protocol parse failure handling, and safe text rendering.
9. Manual verify against running agent: startup, no-agent state, reconnect after agent restart, answer rendering after final transcript.

## Reconnect Behavior For Local Websocket Hook
- Initial connect immediately on mount.
- If connect fails or socket closes unexpectedly:
  - attempt reconnect with backoff sequence `250ms -> 500ms -> 1000ms -> 2000ms -> 4000ms`
  - cap at `4000ms`
  - reset attempt counter after any successful `open`
- Do not reconnect after intentional user `disconnect()` until user clicks `Reconnect`.
- On reconnect:
  - keep last rendered question/answers visible
  - update transport chip to `reconnecting`
  - replace stale transport message once `open` succeeds
- On parse error:
  - keep socket open
  - set non-fatal UI error banner `Unsupported realtime payload shape` or `Invalid realtime message format`
- On endpoint validation failure:
  - do not open socket; set connection state `disconnected` with actionable local-only message.

## Security Constraints
1. Endpoint builder must allow only `ws://127.0.0.1:<port>` or `ws://localhost:<port>`; reject remote hostnames, `wss://`, query-string secrets, and custom paths for Phase 06.
2. Never read provider keys in web runtime. Only consume non-secret host/port config.
3. Render all transcript, question, answer, and error content as plain text React nodes. No `dangerouslySetInnerHTML`, markdown rendering, or linkification.
4. Do not persist transcripts/answers/errors to `localStorage`, IndexedDB, URL params, analytics, or logs.
5. Treat websocket payloads as untrusted until validated by `web/src/lib/protocol.ts`.
6. Keep error banners generic; do not synthesize stack traces or raw websocket payload dumps into UI.

## Dependency Graph
- Phase 02 complete — protocol frozen at v1. Required before reducer/hook.
- Phase 03 complete — localhost websocket server exists. Required before manual integration test.
- Phase 05 complete — answer event payload exists. Required before answer panel rendering.
- Phase 06 implementation can start now.
- Phase 07 depends on Phase 06 complete plus QA PASS.

## Test And Review Checklist For Phase 06 Gate

### Unit
- [ ] `realtime-session-store` maps each protocol event to expected state mutation.
- [ ] reducer clears partial transcript on `transcript.final`.
- [ ] answer event replaces old Option A/B atomically.
- [ ] endpoint validator rejects remote hosts, non-ws scheme, invalid port.
- [ ] parse error path sets safe UI error without crash.

### Integration
- [ ] websocket hook connects to local mock server and dispatches validated events.
- [ ] abnormal close triggers bounded reconnect backoff.
- [ ] intentional disconnect does not auto-reconnect.
- [ ] reconnect success resets attempt counter.
- [ ] invalid payload does not poison existing rendered state.

### UI
- [ ] overlay shows connection status and agent status separately.
- [ ] long answer text wraps and scrolls inside overlay without layout break.
- [ ] close button hides overlay without losing in-memory state unless page reloads.
- [ ] reconnect button is usable while disconnected/reconnecting.
- [ ] text content renders literally, not as HTML.

### Manual QA Gate
- [ ] With agent offline, overlay shows disconnected state and reconnect CTA.
- [ ] Start agent after page load; overlay reconnects and updates to connected.
- [ ] Stop agent mid-session; last good answer remains visible while transport flips to reconnecting/disconnected.
- [ ] Resume agent; overlay reconnects and accepts new events.
- [ ] Final transcript from agent produces visible question and Option A/B within expected latency envelope.

### Review
- [ ] No file exceeds ~200 LOC without strong reason.
- [ ] No overlap between hook, reducer, and presentational responsibilities.
- [ ] No persistence code added.
- [ ] No remote endpoint capability introduced.
- [ ] No raw HTML rendering path introduced.

## Risk Assessment
- High: web scaffold creep (framework/setup churn) delays actual overlay delivery.
  - Mitigation: use Vite + React + TypeScript only, no Tailwind/Next migration in Phase 06.
- High: reconnect loop creates noisy rerenders or duplicate sockets.
  - Mitigation: single hook owner, explicit cleanup, capped timer, no reconnect after manual disconnect.
- Medium: protocol event ordering causes stale error/status display.
  - Mitigation: reducer applies last-write-wins per event type; do not wipe question/answers on transport faults.
- Medium: long generated answers overflow overlay.
  - Mitigation: fixed panel height, internal scrolling, text wrap, no auto-resize.
- Low: future protocol additive fields break UI assumptions.
  - Mitigation: consume only required v1 fields; ignore unknown metadata.

## Rollback Plan
- If Phase 06 UI destabilizes integration, rollback by removing new `web/` runtime files and returning to the existing `web/src/lib/protocol.ts` only baseline.
- Because Phase 06 is additive and isolated to `web/`, rollback does not affect agent or shared contracts.

## Success Criteria
- Overlay connects to local agent websocket and renders validated realtime data in one compact panel.
- User can always tell: transport state, agent state, current question, Option A, Option B, latest safe error.
- Overlay survives local agent restarts without page reload.
- No transcript/answer data persists beyond page lifetime.

## Next Steps
- After implementation: QA PASS report, tracking docs update, then Phase 07 end-to-end hardening.

## Unresolved Questions
- None for Phase 06 MVP if Vite is accepted as the minimal web runtime scaffold.
