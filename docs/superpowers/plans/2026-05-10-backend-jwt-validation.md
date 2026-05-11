# Backend JWT Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar uma fundação backend autocontida para validar JWTs do Supabase, extrair `user_id` de `sub` e expor um decorator compartilhado `verify_jwt`.

**Architecture:** A implementação fica concentrada num módulo pequeno `backend/auth.py`, separado em erro explícito, decoding de token, extração de `user_id` e decorator compartilhado. Como a branch ainda não possui app Flask real, os testes exercitam um contrato request-like mínimo para provar o comportamento de autenticação sem depender de servidor.

**Tech Stack:** Python 3, PyJWT, functools, dataclasses, unittest

---

### File structure

- Create: `backend/__init__.py` — marca o backend como pacote.
- Create: `backend/requirements.txt` — dependência explícita de `PyJWT`.
- Create: `backend/auth.py` — autenticação compartilhada com decorator e helpers.
- Create: `tests/test_backend_auth.py` — regressões da validação JWT.
- Modify: `README.md` — nota curta sobre validação local de JWT no backend.

### Task 1: Modelar o contrato mínimo de autenticação backend

**Files:**
- Create: `tests/test_backend_auth.py`
- Create: `backend/__init__.py`
- Create: `backend/requirements.txt`

- [ ] **Step 1: Write the failing test**

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class BackendAuthFoundationTest(unittest.TestCase):
    def test_backend_auth_files_exist(self):
        required = [
            ROOT / "backend" / "__init__.py",
            ROOT / "backend" / "requirements.txt",
            ROOT / "tests" / "test_backend_auth.py",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_backend_requirements_include_pyjwt(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("PyJWT==", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py -v`
Expected: FAIL with missing backend auth files

- [ ] **Step 3: Write minimal implementation**

Create `backend/__init__.py`:

```python
"""Backend package for Sprint 1 JWT validation."""
```

Create `backend/requirements.txt`:

```text
PyJWT==2.9.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py -v`
Expected: PASS with 2 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_backend_auth.py backend/__init__.py backend/requirements.txt
git commit -m "feat: add backend JWT auth foundation files" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Implementar o núcleo compartilhado de validação JWT

**Files:**
- Modify: `tests/test_backend_auth.py`
- Create: `backend/auth.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_backend_auth.py`:

```python
import importlib.util
import jwt


class BackendJwtCoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = ROOT / "backend" / "auth.py"
        spec = importlib.util.spec_from_file_location("backend.auth", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_decode_supabase_jwt_accepts_valid_token(self):
        token = jwt.encode({"sub": "user-123"}, "secret", algorithm="HS256")
        claims = self.module.decode_supabase_jwt(token, "secret")
        self.assertEqual(claims["sub"], "user-123")

    def test_extract_user_id_returns_sub(self):
        self.assertEqual(self.module.extract_user_id({"sub": "user-123"}), "user-123")

    def test_extract_user_id_rejects_missing_sub(self):
        with self.assertRaises(self.module.AuthError):
            self.module.extract_user_id({})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py -v`
Expected: FAIL with missing `backend/auth.py`

- [ ] **Step 3: Write minimal implementation**

Create `backend/auth.py`:

```python
import jwt


class AuthError(Exception):
    """Raised when backend authentication fails."""


def decode_supabase_jwt(token, jwt_secret):
    try:
        return jwt.decode(token, jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthError("invalid token") from exc


def extract_user_id(claims):
    user_id = claims.get("sub")
    if not user_id:
        raise AuthError("missing sub claim")
    return user_id
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py -v`
Expected: PASS with 5 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_backend_auth.py backend/auth.py
git commit -m "feat: add backend JWT validation core" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Adicionar o decorator compartilhado `verify_jwt`

**Files:**
- Modify: `tests/test_backend_auth.py`
- Modify: `backend/auth.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_backend_auth.py`:

```python
from dataclasses import dataclass


@dataclass
class FakeRequest:
    headers: dict
    user_id: str | None = None


class BackendVerifyJwtDecoratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = ROOT / "backend" / "auth.py"
        spec = importlib.util.spec_from_file_location("backend.auth", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_verify_jwt_rejects_missing_authorization_header(self):
        request = FakeRequest(headers={})

        @self.module.verify_jwt("secret")
        def handler(current_request):
            return current_request.user_id

        with self.assertRaises(self.module.AuthError):
            handler(request)

    def test_verify_jwt_injects_user_id_from_sub_claim(self):
        token = jwt.encode({"sub": "user-123"}, "secret", algorithm="HS256")
        request = FakeRequest(headers={"Authorization": f"Bearer {token}"})

        @self.module.verify_jwt("secret")
        def handler(current_request):
            return current_request.user_id

        self.assertEqual(handler(request), "user-123")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py -v`
Expected: FAIL because `verify_jwt` does not exist yet

- [ ] **Step 3: Write minimal implementation**

Update `backend/auth.py` to:

```python
import jwt
from functools import wraps


class AuthError(Exception):
    """Raised when backend authentication fails."""


def decode_supabase_jwt(token, jwt_secret):
    try:
        return jwt.decode(token, jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthError("invalid token") from exc


def extract_user_id(claims):
    user_id = claims.get("sub")
    if not user_id:
        raise AuthError("missing sub claim")
    return user_id


def _extract_bearer_token(request):
    header = request.headers.get("Authorization", "")
    prefix = "Bearer "
    if not header.startswith(prefix):
        raise AuthError("missing bearer token")
    return header[len(prefix):]


def verify_jwt(jwt_secret):
    def decorator(handler):
        @wraps(handler)
        def wrapped(request, *args, **kwargs):
            token = _extract_bearer_token(request)
            claims = decode_supabase_jwt(token, jwt_secret)
            request.user_id = extract_user_id(claims)
            return handler(request, *args, **kwargs)

        return wrapped

    return decorator
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py -v`
Expected: PASS with 7 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_backend_auth.py backend/auth.py
git commit -m "feat: add shared verify_jwt decorator" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 4: Documentar a política de validação local

**Files:**
- Modify: `tests/test_backend_auth.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_backend_auth.py`:

```python
class BackendJwtReadmeTest(unittest.TestCase):
    def test_readme_documents_backend_jwt_validation(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("verify_jwt", content)
        self.assertIn("SUPABASE_JWT_SECRET", content)
        self.assertIn("sub", content)
        self.assertIn("JWT", content)
        self.assertIn("without querying the database", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py -v`
Expected: FAIL because `README.md` does not yet describe backend JWT validation

- [ ] **Step 3: Write minimal implementation**

Update `README.md` to:

```md
# simples-editor

## Backend JWT validation

Sprint 1 validates Supabase JWTs in the backend with a shared `verify_jwt` mechanism.

The backend depends on:

- `SUPABASE_JWT_SECRET`

The validator decodes the JWT locally, extracts `user_id` from the `sub` claim, and protects backend handlers without querying the database for each request.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_auth.py -v`
Expected: PASS with 8 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_backend_auth.py README.md
git commit -m "docs: describe backend JWT validation" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
