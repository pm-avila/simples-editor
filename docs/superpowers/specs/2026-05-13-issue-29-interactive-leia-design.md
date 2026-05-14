# Issue #29 Design — IDE Leia End-to-End Interaction

## Context
The didactic IDE value depends on interactive `leia` flows where terminal input continues program execution.

## Goals
- Connect frontend terminal input to backend WebSocket `stdin`.
- Render backend `stdout` back into terminal pane.
- Validate end-to-end leia prompt/input continuation contract.

## Non-goals
- Protocol expansion beyond needed integration events.

## Design
1. Add a frontend run-session client module that:
   - opens `/ws/run` WebSocket;
   - sends `compile_and_run` and `stdin`;
   - exposes callbacks for `stdout` and state events.
2. Integrate client in `IdeShell`:
   - create session on Run;
   - send terminal onData to `stdin`;
   - append stdout in terminal pane.
3. Keep graceful fallback for disconnected/non-running session.

## Validation
- Contract tests assert:
  - `handleTerminalData` relays stdin through run-session client.
  - websocket stdout callback writes terminal output.
  - leia-style flow (prompt then input) is represented in integration contract tests.
