## Code Review Summary

### Scope
- Files: `/Users/february10/Documents/interviewCopilot/web/src/main.tsx`, `/Users/february10/Documents/interviewCopilot/web/src/app.tsx`, `/Users/february10/Documents/interviewCopilot/web/src/components/floating-overlay-panel.tsx`, `/Users/february10/Documents/interviewCopilot/web/src/hooks/use-local-agent-websocket.ts`, `/Users/february10/Documents/interviewCopilot/web/src/state/realtime-session-store.ts`, `/Users/february10/Documents/interviewCopilot/web/src/lib/local-agent-url.ts`, `/Users/february10/Documents/interviewCopilot/web/src/lib/protocol.ts`, `/Users/february10/Documents/interviewCopilot/web/src/styles/overlay.css`, `/Users/february10/Documents/interviewCopilot/web/src/test/realtime-session-store.test.ts`, `/Users/february10/Documents/interviewCopilot/web/src/test/use-local-agent-websocket.test.tsx`, `/Users/february10/Documents/interviewCopilot/web/src/test/floating-overlay-panel.test.tsx`, `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts`
- LOC: ~912 reviewed in scoped files
- Focus: Phase 06 code-review gate for web overlay realtime client
- Scout findings: affected dependents are `/Users/february10/Documents/interviewCopilot/agent/message_router.py` and `/Users/february10/Documents/interviewCopilot/agent/ws_hub.py`; key edge cases reviewed were delayed `answer.generated` arrival after a newer `transcript.final`, websocket reconnect churn, invalid payload handling, localhost-only endpoint construction, and plain-text rendering safety.

### Overall Assessment
FAIL. The implementation is close to MVP and the security posture is mostly correct: the client only constructs `ws://localhost|127.0.0.1:<port>`, protocol validation happens before reducer dispatch, and I found no HTML rendering path. However, there is one blocking async ordering bug that can pass unit tests but mispair answers with the wrong question in production when answer generation lags behind newer transcripts.

### Critical Issues
1. Stale `answer.generated` events can overwrite the currently displayed question and answers after a newer question has already arrived.
   - Files:
     - `/Users/february10/Documents/interviewCopilot/web/src/state/realtime-session-store.ts:70-81`
     - `/Users/february10/Documents/interviewCopilot/web/src/state/realtime-session-store.ts:57-63`
     - `/Users/february10/Documents/interviewCopilot/web/src/hooks/use-local-agent-websocket.ts:71-75`
   - Impact: production race condition. The reducer unconditionally applies every `answer.generated` payload and also rewrites `finalQuestion` from `payload.sourceText`, so an older answer arriving late can replace a newer question already shown by `transcript.final`. This creates a trust-boundary/UI correctness failure: the overlay can present answers for question N while the user is currently on question N+1.
   - Why this is realistic: the downstream producer emits `transcript.final` first and only later emits `answer.generated` after async answer generation work. Evidence from scout:
     ```py
     # /Users/february10/Documents/interviewCopilot/agent/message_router.py:40-71
     await hub.broadcast("transcript.final", {...})
     pipeline = process_final_transcript(result.text, config)
     await hub.broadcast("intent.detected", {...})
     answer = await generate_answer_payload(result.text, pipeline, config)
     await hub.broadcast("answer.generated", {...})
     ```
   - Current blocking code:
     ```ts
     // /Users/february10/Documents/interviewCopilot/web/src/state/realtime-session-store.ts:70-79
     case EVENT_TYPES.ANSWER_GENERATED:
       return {
         ...state,
         finalQuestion: event.payload.sourceText,
         questionType: event.payload.questionType,
         optionA: event.payload.optionA,
         optionB: event.payload.optionB,
         answerLanguage: event.payload.language,
         fallbackUsed: event.payload.fallbackUsed,
         qcStatus: event.payload.qcStatus,
       }
     ```
   - Required fix: keep enough causal state to reject stale answers, e.g. only accept `answer.generated` when `payload.sourceText` matches the latest finalized question still on screen, or track a monotonic event/timestamp cursor per question before replacing answers.

### High Priority
1. Error events do not transition agent state to `error`, so UI status can stay stale and misleading after an `error` payload.
   - File: `/Users/february10/Documents/interviewCopilot/web/src/state/realtime-session-store.ts:82-87`
   - Impact: non-blocking for gate, but operator-facing reliability issue. The plan explicitly called out special handling for `error`; current reducer only sets `errorMessage` and `statusMessage`.
2. Hide/close does not control websocket lifecycle; the hook stays connected and can continue receiving transcripts while the overlay is closed.
   - Files:
     - `/Users/february10/Documents/interviewCopilot/web/src/app.tsx:33-46`
     - `/Users/february10/Documents/interviewCopilot/web/src/hooks/use-local-agent-websocket.ts:105-114`
   - Impact: non-blocking for gate, but surprising behavior and unnecessary background activity. The Phase 06 plan described connecting when visible.

### Medium Priority
1. Endpoint validation failure would throw during render instead of surfacing a safe disconnected-state message.
   - File: `/Users/february10/Documents/interviewCopilot/web/src/hooks/use-local-agent-websocket.ts:29`
   - Impact: if host/port become configurable later, invalid local config will crash the component rather than fail closed with actionable UI.
2. Test coverage is too narrow for the reducer and websocket edge cases that matter most.
   - Files:
     - `/Users/february10/Documents/interviewCopilot/web/src/test/realtime-session-store.test.ts:7-40`
     - `/Users/february10/Documents/interviewCopilot/web/src/test/use-local-agent-websocket.test.tsx:46-83`
   - Impact: current tests do not exercise stale answer ordering, parse-error UI preservation, invalid endpoint handling, or separate agent-state/error-state transitions.

### Low Priority
1. `/Users/february10/Documents/interviewCopilot/web/src/components/floating-overlay-panel.tsx` is compact and readable, but list item keys use raw line text.
   - File: `/Users/february10/Documents/interviewCopilot/web/src/components/floating-overlay-panel.tsx:49-60`
   - Impact: duplicate answer lines would cause React key collisions; low severity for current MVP.

### Edge Cases Found by Scout
- Delayed `answer.generated` can arrive after a newer `transcript.final` because answer creation is async downstream.
- Invalid JSON / invalid payload handling is safe at the websocket boundary: `/Users/february10/Documents/interviewCopilot/web/src/lib/protocol.ts:59-86` emits generic parse errors and keeps the socket open.
- Localhost-only constraint is enforced in `/Users/february10/Documents/interviewCopilot/web/src/lib/local-agent-url.ts:3-14`; no remote host, custom path, query string, or `wss://` path is available through this builder.
- I found no HTML rendering path in scoped web source. Grep for `dangerouslySetInnerHTML`, `innerHTML`, markdown rendering, linkification, `localStorage`, `sessionStorage`, and `indexedDB` returned no matches under `/Users/february10/Documents/interviewCopilot/web/src`.
- `answer.generated` payload contract is aligned between producer and validator. Producer fields in `/Users/february10/Documents/interviewCopilot/agent/message_router.py:61-69` match `/Users/february10/Documents/interviewCopilot/shared/realtime-event-contracts.ts:52-63`.

### Positive Observations
- The protocol boundary is correctly centralized. Evidence:
  ```ts
  // /Users/february10/Documents/interviewCopilot/web/src/lib/protocol.ts:59-86
  export const createRealtimeMessageHandler =
    (onEvent, onError) =>
    (rawMessage: string): void => {
      ...
      for (const event of events) {
        onEvent(event)
      }
    }
  ```
- Local-only websocket URL construction is explicit and easy to audit. Evidence:
  ```ts
  // /Users/february10/Documents/interviewCopilot/web/src/lib/local-agent-url.ts:3-13
  export const buildLocalAgentWebSocketUrl = (port: number, host = '127.0.0.1'): string => {
    const normalizedHost = host.trim().toLowerCase()
    if (!LOCAL_HOSTS.has(normalizedHost)) {
      throw new Error('Local agent websocket host must be localhost or 127.0.0.1')
    }
    return `ws://${normalizedHost}:${port}`
  }
  ```
- Plain-text rendering posture is good. The panel renders React text nodes only, e.g. `/Users/february10/Documents/interviewCopilot/web/src/components/floating-overlay-panel.tsx:40-69`, and no unsafe HTML API was found.
- Scoped tests pass locally: `npm --prefix "/Users/february10/Documents/interviewCopilot/web" test -- --run`.

### Recommended Actions
1. Fix the stale-answer race in `/Users/february10/Documents/interviewCopilot/web/src/state/realtime-session-store.ts` before promoting Phase 06.
2. Add a regression test proving that an older `answer.generated` cannot overwrite a newer finalized question.
3. Add reducer coverage for `error` event ordering and parse-error preservation.
4. Optionally align overlay visibility with websocket lifecycle or explicitly document that hiding the panel keeps the session live.

### Metrics
- Type Coverage: not measured in this review
- Test Coverage: 3 scoped Vitest tests passed, but concurrency/error-path coverage remains insufficient
- Linting Issues: not measured in this review
- Test Result: PASS for `/Users/february10/Documents/interviewCopilot/web` scoped test run

### Unresolved Questions
- Is the intended product behavior to keep consuming realtime events while the overlay is hidden, or should hide suspend the websocket until reopened?

### Gate Verdict
FAIL
