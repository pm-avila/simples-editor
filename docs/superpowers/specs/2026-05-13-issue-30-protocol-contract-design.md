# Issue #30 Design — Run-Session WebSocket Protocol Contract

## Context
Frontend and backend need a stable event/command contract to orchestrate compile/run lifecycle, interactive I/O, keepalive and invalid-state handling.

## Goals
- Backend emits: `compile_started`, `asm_generated`, `exec_started`, `stdout`, `exit`, `timeout`.
- Client commands handled: `compile_and_run`, `stdin`, `stop`, `ping`.
- Invalid-state messages are handled safely without closing the connection.

## Non-goals
- Reworking authentication handshake format.

## Design
1. Extend run-session dispatcher with explicit event helpers.
2. Implement protocol transitions:
   - `compile_and_run` ⇒ compile_started → asm_generated → exec_started.
   - running output emits `stdout`.
   - `stop` emits `exit` and resets idle.
3. Keep `ping` → `pong`.
4. For out-of-state commands emit `invalid_state` event and continue loop.
5. If execution bootstrap fails, emit `timeout` fallback and continue.

## Validation
- Contract tests covering event order and command handling.
- Transition tests for invalid-state commands and connection persistence.
