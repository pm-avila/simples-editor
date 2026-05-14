# Supabase Login Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar um frontend mínimo autocontido com login por email/senha via Supabase e uma shell protegida da IDE liberada após autenticação.

**Architecture:** A implementação usa uma UI estática simples e módulos JavaScript pequenos para evitar introduzir um toolchain de frontend completo numa `dev` ainda vazia. O fluxo fica dividido entre configuração pública (`frontend/config.js`), comportamento de autenticação (`frontend/app.js`), marcação da interface (`frontend/index.html`) e uma suíte stdlib-only que valida o contrato estrutural do login.

**Tech Stack:** HTML, JavaScript ES modules, Supabase JS client, Python 3 stdlib + unittest, Markdown

---

### File structure

- Create: `frontend/index.html` — tela de login e shell protegida da IDE.
- Create: `frontend/config.js` — configuração pública do frontend com `SUPABASE_URL` e `SUPABASE_ANON_KEY`.
- Create: `frontend/app.js` — inicialização do cliente Supabase, login e alternância de estado da UI.
- Create: `tests/test_supabase_login_flow.py` — suíte estrutural para o contrato do login.
- Modify: `README.md` — instruções curtas de configuração do login do frontend.

### Task 1: Modelar a UI mínima de login e a configuração pública

**Files:**
- Create: `tests/test_supabase_login_flow.py`
- Create: `frontend/index.html`
- Create: `frontend/config.js`

- [ ] **Step 1: Write the failing test**

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SupabaseLoginUiTest(unittest.TestCase):
    def test_login_ui_and_public_config_exist(self):
        required = [
            ROOT / "frontend" / "index.html",
            ROOT / "frontend" / "config.js",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_login_page_has_email_password_and_ide_shell(self):
        content = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        self.assertIn('type="email"', content)
        self.assertIn('type="password"', content)
        self.assertIn('id="login-form"', content)
        self.assertIn('id="ide-shell"', content)
        self.assertIn("IDE access granted", content)

    def test_public_frontend_config_exposes_supabase_url_and_anon_key(self):
        content = (ROOT / "frontend" / "config.js").read_text(encoding="utf-8")
        self.assertIn("SUPABASE_URL", content)
        self.assertIn("SUPABASE_ANON_KEY", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py -v`
Expected: FAIL with missing `frontend/index.html` or `frontend/config.js`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Simples Editor Login</title>
  </head>
  <body>
    <main>
      <section id="login-screen">
        <h1>Sign in to Simples Editor</h1>
        <form id="login-form">
          <label>
            Email
            <input type="email" id="email" name="email" required />
          </label>
          <label>
            Password
            <input type="password" id="password" name="password" required />
          </label>
          <button type="submit">Sign in</button>
        </form>
        <p id="login-message" role="status"></p>
      </section>

      <section id="ide-shell" hidden>
        <h2>IDE access granted</h2>
        <p>You are authenticated and can access the Sprint 1 IDE shell.</p>
      </section>
    </main>
    <script type="module" src="./app.js"></script>
  </body>
</html>
```

Create `frontend/config.js`:

```javascript
export const SUPABASE_URL = window.__SUPABASE_URL__ || "https://example.supabase.co";
export const SUPABASE_ANON_KEY = window.__SUPABASE_ANON_KEY__ || "dev-anon-key";
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py -v`
Expected: PASS with 3 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_supabase_login_flow.py frontend/index.html frontend/config.js
git commit -m "feat: add Supabase login UI scaffold" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Implementar o fluxo de autenticação com Supabase

**Files:**
- Modify: `tests/test_supabase_login_flow.py`
- Create: `frontend/app.js`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_supabase_login_flow.py`:

```python
class SupabaseLoginFlowScriptTest(unittest.TestCase):
    def test_app_js_uses_supabase_client_and_password_sign_in(self):
        content = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
        self.assertIn("createClient", content)
        self.assertIn("signInWithPassword", content)
        self.assertIn("SUPABASE_URL", content)
        self.assertIn("SUPABASE_ANON_KEY", content)

    def test_app_js_restores_session_and_reveals_ide_shell(self):
        content = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
        self.assertIn("getSession", content)
        self.assertIn("login-form", content)
        self.assertIn("ide-shell", content)
        self.assertIn(".hidden", content.replace(" ", ""))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py -v`
Expected: FAIL with missing `frontend/app.js`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/app.js`:

```javascript
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { SUPABASE_URL, SUPABASE_ANON_KEY } from "./config.js";


const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const loginForm = document.getElementById("login-form");
const loginScreen = document.getElementById("login-screen");
const ideShell = document.getElementById("ide-shell");
const message = document.getElementById("login-message");


function showIdeShell() {
  loginScreen.hidden = true;
  ideShell.hidden = false;
}


function showLoginScreen() {
  loginScreen.hidden = false;
  ideShell.hidden = true;
}


async function restoreSession() {
  const { data } = await supabase.auth.getSession();
  if (data.session) {
    showIdeShell();
    return;
  }
  showLoginScreen();
}


loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const { error } = await supabase.auth.signInWithPassword({
    email: formData.get("email"),
    password: formData.get("password"),
  });

  if (error) {
    message.textContent = error.message;
    showLoginScreen();
    return;
  }

  message.textContent = "";
  showIdeShell();
});


restoreSession();
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py -v`
Expected: PASS with 5 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_supabase_login_flow.py frontend/app.js
git commit -m "feat: add Supabase login flow script" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Documentar a configuração do login

**Files:**
- Modify: `tests/test_supabase_login_flow.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_supabase_login_flow.py`:

```python
class SupabaseLoginReadmeTest(unittest.TestCase):
    def test_readme_documents_frontend_login_setup(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Supabase login", content)
        self.assertIn("SUPABASE_URL", content)
        self.assertIn("SUPABASE_ANON_KEY", content)
        self.assertIn("email/password", content)
        self.assertIn("IDE access granted", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py -v`
Expected: FAIL because `README.md` does not yet describe the frontend login flow

- [ ] **Step 3: Write minimal implementation**

Update `README.md` to:

```md
# simples-editor

## Supabase login

Sprint 1 uses Supabase email/password authentication in the frontend before releasing access to the IDE shell.

The frontend login flow depends on:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

Configure those values before loading the login page. The form sends email/password credentials to Supabase and reveals the protected “IDE access granted” shell after a valid session exists.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py -v`
Expected: PASS with 6 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_supabase_login_flow.py README.md
git commit -m "docs: describe Supabase login flow" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
