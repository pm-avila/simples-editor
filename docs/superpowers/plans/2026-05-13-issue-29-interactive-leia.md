# Interactive Leia IDE Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable end-to-end interactive `leia` behavior by wiring frontend terminal input/output with backend run-session websocket commands/events.

**Architecture:** Introduce a lightweight `run-session-client` in frontend lib and integrate it into `IdeShell` lifecycle. Keep terminal-pane as I/O surface and route stdin/stdout through callbacks.

**Tech Stack:** TypeScript React, WebSocket browser API, Python contract tests (static/source verification)

---

### Task 1: Add failing integration contract tests

**Files:**
- Modify: `tests/test_terminal_xterm_integration.py`

- [ ] **Step 1: Write failing source-contract tests for run-session client integration**
- [ ] **Step 2: Run test file and confirm failure**
Run: `python3 -m unittest tests/test_terminal_xterm_integration.py -v`
Expected: FAIL because websocket client wiring does not exist yet.

- [ ] **Step 3: Implement run-session frontend client + ide wiring**
- [ ] **Step 4: Run the same tests and verify pass**

- [ ] **Step 5: Commit**
```bash
git add frontend/src/lib/run-session-client.ts frontend/src/components/ide/ide-shell.tsx tests/test_terminal_xterm_integration.py
git commit -m "feat(interactive): wire leia stdin/stdout end-to-end in IDE"
```
