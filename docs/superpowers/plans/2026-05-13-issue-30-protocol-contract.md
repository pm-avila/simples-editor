# Run Session Protocol Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and verify the run-session WebSocket event contract for compile/run lifecycle, interactive commands, and invalid-state safety.

**Architecture:** Expand `backend/ws/run_session.py` message handling into explicit protocol transitions and keep state-machine checks central. Validate with focused websocket contract tests in `tests/test_ws_run_auth.py`.

**Tech Stack:** Python websocket session loop, unittest, JSON protocol contracts

---

### Task 1: Add failing protocol contract tests

**Files:**
- Modify: `tests/test_ws_run_auth.py`

- [ ] **Step 1: Add tests for compile/event sequence and stop/ping handling**
- [ ] **Step 2: Run tests to verify failures**
Run: `python3 -m unittest tests/test_ws_run_auth.py -v`
Expected: FAIL due missing events and command handling.

- [ ] **Step 3: Implement protocol transitions in run_session**
- [ ] **Step 4: Re-run tests and confirm pass**

- [ ] **Step 5: Commit**
```bash
git add backend/ws/run_session.py tests/test_ws_run_auth.py
git commit -m "feat(protocol): implement run-session websocket event contract"
```
