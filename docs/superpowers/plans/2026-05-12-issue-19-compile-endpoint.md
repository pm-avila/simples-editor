# Issue #19 — Implement POST /api/compile Endpoint

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expor `POST /api/compile` que invoca `simplesc` e retorna o NASM gerado ou erro estruturado.

**Architecture:** Novo módulo `backend/compiler.py` encapsula subprocess + parsing de erros. A rota é adicionada em `backend/app.py`. Testes mockam subprocess.

**Tech Stack:** Flask, Python subprocess, unittest.mock

---

## File Map

| Ação | Arquivo |
|---|---|
| Create | `backend/compiler.py` |
| Modify | `backend/app.py` |
| Create | `tests/test_compile_endpoint.py` |

---

### Task 1: Criar `backend/compiler.py`

**Files:**
- Create: `backend/compiler.py`

- [ ] **Step 1: Criar `backend/compiler.py`**

```python
"""
Compiler service — wraps simplesc invocation via subprocess.
"""
import os
import re
import subprocess
import tempfile

SIMPLESC_BIN = os.environ.get("SIMPLESC_BIN", "/usr/local/bin/simplesc")
COMPILE_TIMEOUT = int(os.environ.get("COMPILE_TIMEOUT", "15"))

_ERROR_RE = re.compile(r"^(\d+):(\d+):\s*(?:erro:\s*)?(.+)$", re.MULTILINE)


def compile_simples(code: str) -> dict:
    """Compile SIMPLES source to NASM assembly.

    Returns:
        {"ok": True,  "nasm": "<str>"}
        {"ok": False, "error": {"phase": "compile", "line": N, "column": N, "message": "..."}}
    """
    with tempfile.TemporaryDirectory(prefix="sim-") as tmpdir:
        src_path = os.path.join(tmpdir, "programa.simples")
        asm_path = os.path.join(tmpdir, "programa.asm")

        with open(src_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            result = subprocess.run(
                [SIMPLESC_BIN, src_path, "-o", asm_path],
                capture_output=True,
                text=True,
                timeout=COMPILE_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": {
                    "phase": "compile",
                    "line": 0,
                    "column": 0,
                    "message": "timeout: compilação excedeu o limite de tempo",
                },
            }

        if result.returncode != 0:
            return {"ok": False, "error": _parse_compiler_error(result.stderr)}

        with open(asm_path, "r", encoding="utf-8") as f:
            nasm = f.read()

        return {"ok": True, "nasm": nasm}


def _parse_compiler_error(stderr: str) -> dict:
    """Parse compiler stderr line into a structured error dict."""
    match = _ERROR_RE.search(stderr)
    if match:
        return {
            "phase": "compile",
            "line": int(match.group(1)),
            "column": int(match.group(2)),
            "message": match.group(3).strip(),
        }
    return {
        "phase": "compile",
        "line": 0,
        "column": 0,
        "message": stderr.strip() or "compilation failed",
    }
```

- [ ] **Step 2: Commit**

```bash
git add backend/compiler.py
git commit -m "feat(compile): add compiler.py with compile_simples and error parser"
```

---

### Task 2: Escrever testes para o endpoint (TDD)

**Files:**
- Create: `tests/test_compile_endpoint.py`

- [ ] **Step 1: Criar `tests/test_compile_endpoint.py`**

```python
"""
Tests for POST /api/compile endpoint.

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compile_endpoint.py -v
"""
import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from backend.app import app


SAMPLE_NASM = "section .text\n    global _start\n_start:\n    int 0x80\n"


def _mock_success(nasm_content):
    """Return a patch that makes simplesc write nasm_content and exit 0."""
    def fake_run(cmd, capture_output, text, timeout):
        # Write NASM to the output file argument (last arg)
        output_path = cmd[cmd.index("-o") + 1]
        with open(output_path, "w") as f:
            f.write(nasm_content)
        proc = MagicMock()
        proc.returncode = 0
        proc.stderr = ""
        return proc
    return fake_run


def _mock_failure(stderr, returncode=1):
    """Return a patch that makes simplesc fail with stderr and given returncode."""
    def fake_run(cmd, capture_output, text, timeout):
        proc = MagicMock()
        proc.returncode = returncode
        proc.stderr = stderr
        return proc
    return fake_run


class TestCompileEndpointSuccess(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_compile_returns_nasm_on_success(self):
        with patch("backend.compiler.subprocess.run", side_effect=_mock_success(SAMPLE_NASM)):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("nasm", body)
        self.assertEqual(body["nasm"], SAMPLE_NASM)

    def test_post_compile_success_has_no_error_key(self):
        with patch("backend.compiler.subprocess.run", side_effect=_mock_success(SAMPLE_NASM)):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        self.assertNotIn("error", resp.get_json())


class TestCompileEndpointFailure(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_compile_returns_422_on_compiler_error(self):
        stderr = "4:7: erro: variavel 'y' nao declarada"
        with patch("backend.compiler.subprocess.run", side_effect=_mock_failure(stderr)):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 422)

    def test_post_compile_error_has_structured_fields(self):
        stderr = "4:7: erro: variavel 'y' nao declarada"
        with patch("backend.compiler.subprocess.run", side_effect=_mock_failure(stderr)):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        error = resp.get_json()["error"]
        self.assertEqual(error["line"], 4)
        self.assertEqual(error["column"], 7)
        self.assertIn("variavel", error["message"])
        self.assertEqual(error["phase"], "compile")

    def test_post_compile_timeout_returns_422(self):
        def fake_timeout(cmd, capture_output, text, timeout):
            raise subprocess.TimeoutExpired(cmd, timeout)

        with patch("backend.compiler.subprocess.run", side_effect=fake_timeout):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 422)
        self.assertIn("timeout", resp.get_json()["error"]["message"])


class TestCompileEndpointValidation(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_compile_empty_code_returns_400(self):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({"code": ""}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_compile_missing_code_returns_400(self):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_compile_whitespace_only_returns_400(self):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({"code": "   \n  "}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Executar testes (esperar FALHA — rota ainda não existe)**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compile_endpoint.py -v
```

Esperado: erros de `404` ou `AttributeError` porque `POST /api/compile` não existe.

---

### Task 3: Adicionar rota `POST /api/compile` ao `backend/app.py`

**Files:**
- Modify: `backend/app.py`

- [ ] **Step 1: Atualizar `backend/app.py`**

```python
from flask import Flask, jsonify, request

from backend.compiler import compile_simples
from backend.health import build_health_payload


app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "ok"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/health")
def api_health():
    return jsonify(build_health_payload())


@app.post("/api/compile")
def api_compile():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not code or not code.strip():
        return jsonify({"error": "código vazio"}), 400

    result = compile_simples(code)
    if result["ok"]:
        return jsonify({"nasm": result["nasm"]}), 200
    return jsonify({"error": result["error"]}), 422


def create_app():
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

- [ ] **Step 2: Executar todos os testes (esperar PASS)**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compile_endpoint.py -v
```

Esperado: 8 testes passam.

- [ ] **Step 3: Garantir testes anteriores ainda passam**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_dockerfile.py tests/test_health_endpoint.py -v
```

Esperado: todos passam.

- [ ] **Step 4: Commit**

```bash
git add backend/app.py tests/test_compile_endpoint.py docs/superpowers/specs/2026-05-12-issue-19-compile-endpoint-design.md docs/superpowers/plans/2026-05-12-issue-19-compile-endpoint.md
git commit -m "feat(compile): implement POST /api/compile endpoint

- Novo backend/compiler.py com compile_simples() e _parse_compiler_error()
- Rota POST /api/compile em app.py
- 8 testes cobrindo sucesso, erro estruturado, timeout e validação

Closes #19

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Self-Review

**Spec coverage:**
- ✅ `POST /api/compile` existe
- ✅ Aceita código SIMPLES via JSON
- ✅ Sucesso → 200 `{"nasm": "..."}`
- ✅ Falha → 422 `{"error": {...}}`
- ✅ Erro estruturado (não genérico)

**Placeholder scan:** Nenhum TBD.

**Type consistency:** `compile_simples` retorna dict com `"ok"`, `"nasm"`, `"error"` — todos os usos no app.py e nos testes são consistentes.
