# Supabase Auth Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Versionar a fundação mínima de auth do Supabase para o v1 em uma branch autocontida, com contrato de ambiente, configuração declarativa, módulo de backend e documentação explícita sobre validação local de JWT.

**Architecture:** A implementação cria uma base declarativa e testável, sem depender de um tenant cloud real. O contrato fica dividido entre `supabase/config.toml` para a configuração do projeto, `.env.example` para as variáveis obrigatórias e `backend/auth_config.py` para centralizar a leitura e a explicação do modelo de autenticação que será consumido nas issues seguintes.

**Tech Stack:** Python 3 stdlib + unittest, TOML textual, Markdown, backend Python

---

### File structure

- Create: `.env.example` — variáveis mínimas de integração com Supabase.
- Create: `supabase/config.toml` — configuração declarativa do projeto Supabase local.
- Create: `backend/__init__.py` — marca o backend como pacote importável.
- Create: `backend/requirements.txt` — dependência explícita para a futura validação local de JWT.
- Create: `backend/auth_config.py` — módulo isolado de leitura/descrição da configuração de auth.
- Create: `tests/test_supabase_auth_foundation.py` — suíte de regressão da issue #5.
- Modify: `README.md` — documentação curta da fundação de auth do v1.

### Task 1: Versionar o contrato mínimo de ambiente e projeto Supabase

**Files:**
- Create: `tests/test_supabase_auth_foundation.py`
- Create: `.env.example`
- Create: `supabase/config.toml`
- Create: `backend/requirements.txt`

- [ ] **Step 1: Write the failing test**

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SupabaseFoundationFilesTest(unittest.TestCase):
    def test_env_and_supabase_contract_files_exist(self):
        required = [
            ROOT / ".env.example",
            ROOT / "supabase" / "config.toml",
            ROOT / "backend" / "requirements.txt",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_env_example_declares_required_supabase_variables(self):
        content = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("SUPABASE_URL=", content)
        self.assertIn("SUPABASE_ANON_KEY=", content)
        self.assertIn("SUPABASE_JWT_SECRET=", content)

    def test_supabase_config_enables_auth_for_local_project(self):
        content = (ROOT / "supabase" / "config.toml").read_text(encoding="utf-8")
        self.assertIn("project_id =", content)
        self.assertIn("[auth]", content)
        self.assertIn("site_url =", content)
        self.assertIn("enable_signup =", content)

    def test_backend_requirements_prepare_local_jwt_validation(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("PyJWT==", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_auth_foundation.py -v`
Expected: FAIL with missing `.env.example`, `supabase/config.toml`, or `backend/requirements.txt`

- [ ] **Step 3: Write minimal implementation**

Create `.env.example`:

```dotenv
SUPABASE_URL=https://example.supabase.co
SUPABASE_ANON_KEY=dev-anon-key
SUPABASE_JWT_SECRET=dev-jwt-secret
```

Create `supabase/config.toml`:

```toml
project_id = "simples-editor"

[auth]
enabled = true
site_url = "http://localhost"
additional_redirect_urls = ["http://localhost"]
jwt_expiry = 3600
enable_signup = true
enable_anonymous_sign_ins = false
```

Create `backend/requirements.txt`:

```text
PyJWT==2.9.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_auth_foundation.py -v`
Expected: PASS with 4 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_supabase_auth_foundation.py .env.example supabase/config.toml backend/requirements.txt
git commit -m "feat: add Supabase auth foundation contract" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Centralizar a configuração de auth do backend

**Files:**
- Modify: `tests/test_supabase_auth_foundation.py`
- Create: `backend/__init__.py`
- Create: `backend/auth_config.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_supabase_auth_foundation.py`:

```python
import importlib.util


class BackendAuthConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = ROOT / "backend" / "auth_config.py"
        spec = importlib.util.spec_from_file_location("backend.auth_config", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_load_supabase_auth_config_returns_expected_fields(self):
        config = self.module.load_supabase_auth_config(
            {
                "SUPABASE_URL": "https://demo.supabase.co",
                "SUPABASE_ANON_KEY": "anon",
                "SUPABASE_JWT_SECRET": "secret",
            }
        )
        self.assertEqual(config.url, "https://demo.supabase.co")
        self.assertEqual(config.anon_key, "anon")
        self.assertEqual(config.jwt_secret, "secret")

    def test_auth_model_summary_explains_local_jwt_validation(self):
        summary = self.module.auth_model_summary()
        self.assertIn("auth.users", summary)
        self.assertIn("JWT", summary)
        self.assertIn("without querying the database", summary)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_auth_foundation.py -v`
Expected: FAIL with missing `backend/auth_config.py`

- [ ] **Step 3: Write minimal implementation**

Create `backend/__init__.py`:

```python
"""Backend package for Sprint 1 auth foundation."""
```

Create `backend/auth_config.py`:

```python
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class SupabaseAuthConfig:
    url: str
    anon_key: str
    jwt_secret: str


def load_supabase_auth_config(env=None):
    source = os.environ if env is None else env
    return SupabaseAuthConfig(
        url=source["SUPABASE_URL"],
        anon_key=source["SUPABASE_ANON_KEY"],
        jwt_secret=source["SUPABASE_JWT_SECRET"],
    )


def auth_model_summary():
    return (
        "Supabase v1 uses auth.users as the identity source, and the backend validates "
        "JWT locally without querying the database."
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_auth_foundation.py -v`
Expected: PASS with 6 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_supabase_auth_foundation.py backend/__init__.py backend/auth_config.py
git commit -m "feat: add backend Supabase auth config module" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Documentar o modelo de auth do v1

**Files:**
- Modify: `tests/test_supabase_auth_foundation.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_supabase_auth_foundation.py`:

```python
class ReadmeSupabaseAuthFoundationTest(unittest.TestCase):
    def test_readme_documents_supabase_auth_foundation(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Supabase", content)
        self.assertIn(".env.example", content)
        self.assertIn("SUPABASE_URL", content)
        self.assertIn("SUPABASE_JWT_SECRET", content)
        self.assertIn("auth.users", content)
        self.assertIn("JWT", content)
        self.assertIn("without querying the database", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_auth_foundation.py -v`
Expected: FAIL because `README.md` does not yet describe the auth foundation

- [ ] **Step 3: Write minimal implementation**

Update `README.md` to:

```md
# simples-editor

## Supabase auth foundation

Sprint 1 uses Supabase as the identity provider for v1. The repository expects the local environment to provide:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`

Copy `.env.example` to `.env` and replace the placeholder values with the project credentials for your Supabase environment.

The authentication model is based on Supabase Auth and its native `auth.users` table. The backend will validate JWT locally with the shared secret, without querying the database for each request.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_auth_foundation.py -v`
Expected: PASS with 7 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_supabase_auth_foundation.py README.md
git commit -m "docs: describe Supabase auth foundation" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
