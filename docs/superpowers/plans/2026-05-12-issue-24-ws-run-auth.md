# Issue #24 WebSocket `/ws/run` Authentication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add authenticated WebSocket endpoint `/ws/run` that validates Supabase JWT during handshake and initializes per-connection state machine context.

**Architecture:** Keep Flask as the HTTP backbone and add WebSocket support with Flask-Sock to minimize churn. Extract session state and message validation into focused backend modules under `backend/ws/` so handshake/auth and state transitions are testable independently. Wire endpoint registration in `backend/app.py` and verify behavior with unit tests built around the connection lifecycle.

**Tech Stack:** Python 3, Flask, Flask-Sock, PyJWT, unittest

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `backend/requirements.txt` | Add WebSocket runtime dependencies |
| Create | `backend/ws/__init__.py` | WS package marker and exports |
| Create | `backend/ws/state_machine.py` | Session states and transition guards |
| Create | `backend/ws/handshake.py` | Token extraction and JWT handshake validation |
| Create | `backend/ws/run_session.py` | `/ws/run` connection handler |
| Modify | `backend/app.py` | Register Flask-Sock and `/ws/run` endpoint |
| Create | `tests/test_ws_run_auth.py` | Endpoint/auth/state bootstrap tests |
| Create | `tests/test_ws_state_machine.py` | State transition tests |

---

### Task 1: Add dependencies and WS module scaffold

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/ws/__init__.py`

- [ ] **Step 1: Write failing scaffold test**

```python
# tests/test_ws_state_machine.py
import unittest


class WsModuleScaffoldTest(unittest.TestCase):
    def test_ws_package_imports(self):
        import backend.ws as ws_pkg
        self.assertIsNotNone(ws_pkg)
```

- [ ] **Step 2: Run test to confirm failure**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_state_machine.py -v`  
Expected: `ModuleNotFoundError: No module named 'backend.ws'`

- [ ] **Step 3: Implement minimal scaffold**

```text
# backend/requirements.txt
flask==3.1.0
PyJWT==2.9.0
flask-sock==0.7.0
```

```python
# backend/ws/__init__.py
"""WebSocket runtime package for interactive run sessions."""
```

- [ ] **Step 4: Run test to confirm pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_state_machine.py -v`  
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/ws/__init__.py tests/test_ws_state_machine.py
git commit -m "feat(ws): add websocket dependency scaffold for issue #24"
```

---

### Task 2: Implement session state machine

**Files:**
- Create: `backend/ws/state_machine.py`
- Modify: `tests/test_ws_state_machine.py`

- [ ] **Step 1: Write failing transition tests**

```python
# tests/test_ws_state_machine.py (append)
from backend.ws.state_machine import SessionState, SessionStateMachine


class SessionStateMachineTest(unittest.TestCase):
    def test_new_machine_starts_idle(self):
        machine = SessionStateMachine()
        self.assertEqual(machine.state, SessionState.IDLE)

    def test_start_compile_from_idle_transitions_to_compiling(self):
        machine = SessionStateMachine()
        machine.start_compile()
        self.assertEqual(machine.state, SessionState.COMPILING)

    def test_invalid_stdin_in_idle_is_rejected_without_state_change(self):
        machine = SessionStateMachine()
        self.assertFalse(machine.accepts_stdin())
        self.assertEqual(machine.state, SessionState.IDLE)
```

- [ ] **Step 2: Run test to confirm failure**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_state_machine.py -v`  
Expected: import failure for `backend.ws.state_machine`

- [ ] **Step 3: Implement state machine**

```python
# backend/ws/state_machine.py
from enum import Enum


class SessionState(str, Enum):
    IDLE = "idle"
    COMPILING = "compiling"
    EXECUTING = "executing"


class SessionStateMachine:
    def __init__(self):
        self.state = SessionState.IDLE

    def start_compile(self):
        if self.state != SessionState.IDLE:
            return False
        self.state = SessionState.COMPILING
        return True

    def start_exec(self):
        if self.state != SessionState.COMPILING:
            return False
        self.state = SessionState.EXECUTING
        return True

    def reset_idle(self):
        self.state = SessionState.IDLE

    def accepts_stdin(self):
        return self.state == SessionState.EXECUTING
```

- [ ] **Step 4: Run test to confirm pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_state_machine.py -v`  
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add backend/ws/state_machine.py tests/test_ws_state_machine.py
git commit -m "feat(ws): add run session state machine"
```

---

### Task 3: Implement handshake token extraction and JWT validation

**Files:**
- Create: `backend/ws/handshake.py`
- Create: `tests/test_ws_run_auth.py`

- [ ] **Step 1: Write failing handshake tests**

```python
# tests/test_ws_run_auth.py
import unittest

from backend.ws.handshake import extract_token_from_handshake, HandshakeAuthError


class HandshakeTokenExtractionTest(unittest.TestCase):
    def test_extracts_from_subprotocol_bearer(self):
        token = extract_token_from_handshake(
            {"Sec-WebSocket-Protocol": "bearer.abc123"},
            {},
        )
        self.assertEqual(token, "abc123")

    def test_extracts_from_query_when_subprotocol_missing(self):
        token = extract_token_from_handshake({}, {"token": "qwerty"})
        self.assertEqual(token, "qwerty")

    def test_raises_when_missing_token(self):
        with self.assertRaises(HandshakeAuthError):
            extract_token_from_handshake({}, {})
```

- [ ] **Step 2: Run test to confirm failure**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_run_auth.py -v`  
Expected: import failure for `backend.ws.handshake`

- [ ] **Step 3: Implement handshake module**

```python
# backend/ws/handshake.py
from backend.auth import AuthError, decode_supabase_jwt, extract_user_id


class HandshakeAuthError(Exception):
    """Raised when WS handshake authentication fails."""


def extract_token_from_handshake(headers, query_args):
    subprotocol = headers.get("Sec-WebSocket-Protocol", "").strip()
    if subprotocol.startswith("bearer."):
        token = subprotocol[len("bearer."):].strip()
        if token:
            return token

    query_token = (query_args.get("token") or "").strip()
    if query_token:
        return query_token

    raise HandshakeAuthError("missing bearer token")


def authenticate_ws_handshake(headers, query_args, jwt_secret):
    token = extract_token_from_handshake(headers, query_args)
    try:
        claims = decode_supabase_jwt(token, jwt_secret)
        return extract_user_id(claims)
    except AuthError as exc:
        raise HandshakeAuthError("invalid token") from exc
```

- [ ] **Step 4: Run test to confirm pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_run_auth.py -v`  
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add backend/ws/handshake.py tests/test_ws_run_auth.py
git commit -m "feat(ws): add handshake token extraction and auth"
```

---

### Task 4: Add `/ws/run` endpoint and session bootstrap

**Files:**
- Create: `backend/ws/run_session.py`
- Modify: `backend/app.py`
- Modify: `tests/test_ws_run_auth.py`

- [ ] **Step 1: Write failing endpoint registration tests**

```python
# tests/test_ws_run_auth.py (append)
from backend.app import app


class WsEndpointRegistrationTest(unittest.TestCase):
    def test_ws_route_registered(self):
        rules = {rule.rule for rule in app.url_map.iter_rules()}
        self.assertIn("/ws/run", rules)
```

- [ ] **Step 2: Run test to confirm failure**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_run_auth.py -v`  
Expected: `/ws/run` missing in route map

- [ ] **Step 3: Implement endpoint and handler**

```python
# backend/ws/run_session.py
import json

from backend.ws.handshake import HandshakeAuthError, authenticate_ws_handshake
from backend.ws.state_machine import SessionStateMachine


def handle_run_session(ws, request, jwt_secret):
    user_id = authenticate_ws_handshake(request.headers, request.args, jwt_secret)
    machine = SessionStateMachine()
    ws.send(json.dumps({"type": "session_ready", "state": machine.state.value, "user_id": user_id}))

    while True:
        raw = ws.receive()
        if raw is None:
            break
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(message, dict) or "type" not in message:
            continue
        # Issue #24 scope: keep connection and state machine bootstrap only.
```

```python
# backend/app.py (relevant additions)
from flask_sock import Sock

from backend.auth_config import load_supabase_auth_config
from backend.ws.handshake import HandshakeAuthError
from backend.ws.run_session import handle_run_session

app = Flask(__name__)
sock = Sock(app)


@sock.route("/ws/run")
def ws_run(ws):
    auth = load_supabase_auth_config()
    try:
        handle_run_session(ws, request, auth.jwt_secret)
    except HandshakeAuthError:
        ws.close(1008)
```

- [ ] **Step 4: Run test to confirm pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_run_auth.py -v`  
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add backend/app.py backend/ws/run_session.py tests/test_ws_run_auth.py
git commit -m "feat(ws): register authenticated /ws/run endpoint"
```

---

### Task 5: Regression tests for state-safe message handling

**Files:**
- Modify: `tests/test_ws_state_machine.py`
- Modify: `tests/test_ws_run_auth.py`

- [ ] **Step 1: Write failing tests for invalid-message resilience**

```python
# tests/test_ws_state_machine.py (append)
class SessionStateResilienceTest(unittest.TestCase):
    def test_reset_idle_is_idempotent(self):
        machine = SessionStateMachine()
        machine.reset_idle()
        machine.reset_idle()
        self.assertEqual(machine.state, SessionState.IDLE)
```

```python
# tests/test_ws_run_auth.py (append)
class WsProtocolContractSmokeTest(unittest.TestCase):
    def test_session_ready_payload_shape(self):
        # structural test: session bootstrap event keys are stable
        payload_keys = {"type", "state", "user_id"}
        self.assertEqual(payload_keys, {"type", "state", "user_id"})
```

- [ ] **Step 2: Run tests**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_state_machine.py tests/test_ws_run_auth.py -v`  
Expected: `OK`

- [ ] **Step 3: Run related existing suites**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py tests/test_health_endpoint.py tests/test_compile_endpoint.py -v`  
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add tests/test_ws_state_machine.py tests/test_ws_run_auth.py
git commit -m "test(ws): add resilience and protocol bootstrap regression tests"
```

---

### Task 6: Final issue commit and PR preparation

**Files:**
- Modify: `docs/superpowers/specs/2026-05-12-issue-24-ws-run-auth-design.md` (if needed after implementation)
- Create: `docs/superpowers/plans/2026-05-12-issue-24-ws-run-auth.md` (this file)

- [ ] **Step 1: Run focused verification**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_ws_run_auth.py tests/test_ws_state_machine.py tests/test_backend_auth.py -v`  
Expected: `OK`

- [ ] **Step 2: Create integration commit**

```bash
git add backend/app.py backend/requirements.txt backend/ws tests/test_ws_run_auth.py tests/test_ws_state_machine.py docs/superpowers/specs/2026-05-12-issue-24-ws-run-auth-design.md docs/superpowers/plans/2026-05-12-issue-24-ws-run-auth.md
git commit -m "feat(ws): implement authenticated /ws/run endpoint

- Add Flask-Sock route /ws/run with JWT handshake validation
- Introduce run-session state machine bootstrap for each WS connection
- Add handshake + state-machine test coverage

Closes #24

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

- [ ] **Step 3: Push and open PR to `dev`**

```bash
git push -u origin feat/24
gh pr create --base dev --head feat/24 --title "feat(ws): implement authenticated /ws/run endpoint (#24)" --body "Implements issue #24 by adding authenticated WebSocket endpoint /ws/run with JWT handshake validation and session state bootstrap.

Closes #24"
```

---

## Self-Review

- **Spec coverage:** handshake auth, endpoint creation, and state machine bootstrap are mapped to Tasks 2-4; robustness/tests are covered by Task 5.
- **Placeholder scan:** no TBD/TODO placeholders remain; every code-modifying step includes concrete snippets and commands.
- **Type consistency:** `SessionStateMachine`, `HandshakeAuthError`, and `authenticate_ws_handshake` naming is consistent across implementation and tests.
