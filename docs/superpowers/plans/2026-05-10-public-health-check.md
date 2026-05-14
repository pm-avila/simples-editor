# Public Health Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar uma fundacao backend autocontida que exponha `GET /api/health` publicamente e retorne um payload JSON minimo de saude do servico.

**Architecture:** A branch `feat/8` vai introduzir um backend Flask pequeno e focado, com a rota HTTP em `backend/app.py` e a construcao do payload em `backend/health.py`. Os testes usarao Flask test client para validar comportamento HTTP real sem depender de Docker, frontend, JWT ou servicos externos.

**Tech Stack:** Python 3, Flask, unittest

---

### File structure

- Create: `backend/__init__.py` — marca o backend como pacote Python.
- Create: `backend/requirements.txt` — declara Flask explicitamente para esta branch autocontida.
- Create: `backend/health.py` — helper pequeno para montar o payload do health check.
- Create: `backend/app.py` — app Flask com `create_app()` e rota publica `GET /api/health`.
- Create: `tests/test_health_endpoint.py` — regressao estrutural, contrato HTTP e documentacao.
- Modify: `README.md` — instrucoes curtas do endpoint e do payload esperado.

### Task 1: Criar a fundacao minima do backend

**Files:**
- Create: `backend/__init__.py`
- Create: `backend/requirements.txt`
- Create: `tests/test_health_endpoint.py`

- [ ] **Step 1: Write the failing test**

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class HealthEndpointFoundationTest(unittest.TestCase):
    def test_required_backend_files_exist(self):
        required = [
            ROOT / "backend" / "__init__.py",
            ROOT / "backend" / "requirements.txt",
            ROOT / "tests" / "test_health_endpoint.py",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_backend_requirements_include_flask(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("flask==", content.lower())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_health_endpoint.py -v`
Expected: FAIL with missing backend foundation files on `feat/8`

- [ ] **Step 3: Write minimal implementation**

Create `backend/__init__.py`:

```python
"""Backend package for Sprint 1 health check."""
```

Create `backend/requirements.txt`:

```text
flask==3.1.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_health_endpoint.py -v`
Expected: PASS with 2 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_health_endpoint.py backend/__init__.py backend/requirements.txt
git commit -m "feat: add backend health check foundation" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Expor `GET /api/health` sem JWT

**Files:**
- Modify: `tests/test_health_endpoint.py`
- Create: `backend/health.py`
- Create: `backend/app.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_health_endpoint.py`:

```python
from backend.app import create_app


class HealthEndpointContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = create_app().test_client()

    def test_get_api_health_returns_ok_status(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_get_api_health_is_public(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.get_json())

    def test_get_api_health_reports_backend_service_name(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.get_json()["service"], "backend")
```

Keep `if __name__ == "__main__": unittest.main()` at the end of the file after appending the new test class.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_health_endpoint.py -v`
Expected: FAIL because `backend.app` does not exist yet

- [ ] **Step 3: Write minimal implementation**

Create `backend/health.py`:

```python
def build_health_payload():
    return {
        "status": "ok",
        "service": "backend",
    }
```

Create `backend/app.py`:

```python
from flask import Flask, jsonify

from backend.health import build_health_payload


def create_app():
    app = Flask(__name__)

    @app.get("/api/health")
    def health():
        return jsonify(build_health_payload())

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_health_endpoint.py -v`
Expected: PASS with 5 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_health_endpoint.py backend/health.py backend/app.py
git commit -m "feat: add public api health endpoint" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Documentar o health check publico

**Files:**
- Modify: `tests/test_health_endpoint.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_health_endpoint.py`:

```python
class HealthEndpointReadmeTest(unittest.TestCase):
    def test_readme_documents_public_health_check(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("/api/health", content)
        self.assertIn("GET", content)
        self.assertIn("status", content)
        self.assertIn("ok", content)
        self.assertIn("without JWT", content)
```

Keep `if __name__ == "__main__": unittest.main()` at the end of the file after appending the new test class.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_health_endpoint.py -v`
Expected: FAIL because `README.md` does not yet document the public health endpoint

- [ ] **Step 3: Write minimal implementation**

Update `README.md` to:

```md
# simples-editor

## Public health check

The backend exposes `GET /api/health` without JWT for local diagnostics and deployment probes.

Expected healthy response:

    {"status": "ok", "service": "backend"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_health_endpoint.py -v`
Expected: PASS with 6 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_health_endpoint.py README.md
git commit -m "docs: describe public health endpoint" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
