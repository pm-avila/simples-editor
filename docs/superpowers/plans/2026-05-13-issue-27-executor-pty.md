# Pty Execution Strategy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a backend execution strategy abstraction and a guarded `PtyExecutionStrategy` skeleton for interactive runs.

**Architecture:** Introduce a small interface and lifecycle model in `backend/ws/execution.py`, then implement `PtyExecutionStrategy` in `backend/ws/pty_execution.py` with explicit guardrails and lazy Docker SDK interaction. Keep behavior test-driven with focused unit tests.

**Tech Stack:** Python 3, unittest, dataclasses, enum, typing Protocol

---

### Task 1: Add failing lifecycle guard tests

**Files:**
- Test: `tests/test_pty_execution_strategy.py`

- [ ] **Step 1: Write failing test**
```python
def test_send_stdin_requires_started_handle(self):
    strategy = PtyExecutionStrategy(...)
    with self.assertRaises(ExecutionStrategyError):
        strategy.send_stdin("x")
```

- [ ] **Step 2: Run test to verify failure**
Run: `python3 -m unittest tests/test_pty_execution_strategy.py -v`
Expected: FAIL because module/class does not exist yet.

- [ ] **Step 3: Implement minimal strategy abstraction and skeleton**
Add `backend/ws/execution.py` and `backend/ws/pty_execution.py`.

- [ ] **Step 4: Run tests to verify pass**
Run: `python3 -m unittest tests/test_pty_execution_strategy.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add backend/ws/execution.py backend/ws/pty_execution.py tests/test_pty_execution_strategy.py
git commit -m "feat(executor): add pty execution strategy skeleton"
```

### Task 2: Regression validation

**Files:**
- Test: `tests/test_ws_state_machine.py`
- Test: `tests/test_ws_run_auth.py`

- [ ] **Step 1: Run focused websocket tests**
Run: `python3 -m unittest tests/test_ws_state_machine.py tests/test_ws_run_auth.py -v`
Expected: PASS.
