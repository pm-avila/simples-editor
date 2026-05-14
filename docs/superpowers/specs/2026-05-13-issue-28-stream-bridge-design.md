# Issue #28 Design — WebSocket ↔ PTY Stream Bridge

## Context
With `PtyExecutionStrategy` in place, run-session needs a bidirectional stream bridge so terminal output/input flows in real time without polling loops.

## Goals
- Forward PTY stdout to WebSocket `stdout` events.
- Relay WebSocket `stdin` messages to PTY input.
- Preserve run-session state safety for invalid timing/state.

## Non-goals
- Frontend terminal integration (issue #29).
- Full protocol matrix finalization (issue #30).

## Design
1. Extend run-session loop to own one execution strategy instance per session.
2. On `compile_and_run`, transition state and start strategy.
3. Emit stdout payloads from strategy output as event messages.
4. On `stdin`, validate state and safely relay data to strategy.
5. For invalid-state `stdin`, emit non-fatal error event (no connection drop).

## Validation
- Unit tests proving:
  - stdout forwarding after start.
  - stdin relay while executing.
  - invalid-state stdin generates safe protocol response.
