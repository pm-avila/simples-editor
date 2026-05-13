# Issue #27 Design — PtyExecutionStrategy

## Context
Interactive execution requires an execution abstraction that can later host multiple strategies while keeping lifecycle/state controls in one place.

## Goals
- Introduce backend execution strategy abstraction.
- Add `PtyExecutionStrategy` skeleton backed by Docker SDK boundaries.
- Protect lifecycle transitions with explicit guards.

## Non-goals
- Full PTY stream bridge (covered by issue #28).
- Frontend integration (covered by issue #29).

## Design
1. Create `backend/ws/execution.py` with:
   - `ExecutionLifecycleState` enum.
   - `ExecutionHandle` dataclass.
   - `ExecutionStrategy` protocol interface.
2. Create `backend/ws/pty_execution.py`:
   - `PtyExecutionStrategy` constructor with optional docker client factory.
   - `start`, `send_stdin`, `stop`, and `poll_stdout` skeleton methods.
   - Strict guard checks for invalid state transitions.
3. Keep implementation safe in environments without Docker SDK by lazy import and explicit `ExecutionStrategyError`.

## Validation
- Unit tests for lifecycle guards:
  - Cannot send stdin before `start`.
  - Cannot start twice.
  - Stop is idempotent and guarded.
  - Errors are normalized as `ExecutionStrategyError`.
