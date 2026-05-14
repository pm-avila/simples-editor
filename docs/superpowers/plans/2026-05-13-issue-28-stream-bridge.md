# Run Session Stream Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bridge terminal I/O between WebSocket messages and PTY strategy in run-session without polling loops.

**Architecture:** Add event-safe bridge logic inside `backend/ws/run_session.py` using the existing state machine and `PtyExecutionStrategy`. Emit protocol events for stdout and invalid-state operations while preserving connection stability.

**Tech Stack:** Python unittest, WebSocket session loop, strategy abstraction

---

### Task 1: Add failing run-session bridge tests

**Files:**
- Modify: `tests/test_ws_run_auth.py`

- [ ] **Step 1: Write failing tests for stdout forwarding and stdin relay**
- [ ] **Step 2: Run focused test selection to confirm failure**
Run: `python3 -m unittest tests/test_ws_run_auth.py -v`
Expected: FAIL on missing stdout/stdin bridge behavior.

- [ ] **Step 3: Implement minimal bridge logic in run_session**
Modify `backend/ws/run_session.py` to:
- start strategy on compile command;
- forward stdout event;
- relay stdin while executing;
- emit invalid-state error message safely.

- [ ] **Step 4: Re-run tests**
Run: `python3 -m unittest tests/test_ws_run_auth.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add backend/ws/run_session.py tests/test_ws_run_auth.py
git commit -m "feat(stream): bridge websocket terminal io with pty strategy"
```
