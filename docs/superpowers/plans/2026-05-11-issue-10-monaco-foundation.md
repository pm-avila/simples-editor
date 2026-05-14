# Issue #10 Monaco Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrar o frontend para uma base React + TypeScript com Monaco na rota principal, preservando o gate atual de login Supabase e preparando a trilha das issues #11 a #16.

**Architecture:** A mudança substitui o frontend estático por uma SPA pequena em React/TypeScript servida pelo container atual. A autenticação continua sendo um gate de sessão Supabase no cliente; quando autenticado, o usuário vê a tela principal da IDE com um Monaco editável como conteúdo central. A estrutura do app deixa pontos claros de extensão para linguagem custom, tema, shell de três painéis, splitters, Run mockado e painel NASM nas próximas PRs.

**Tech Stack:** React 18, TypeScript 5, Vite, TanStack Router, Monaco via `@monaco-editor/react`, Supabase JS 2, Python `unittest`, Docker

---

### File structure

- Create: `frontend/package.json` — dependências e scripts do app React/TypeScript.
- Create: `frontend/tsconfig.json` — tipagem e compilação TypeScript.
- Create: `frontend/vite.config.ts` — build Vite para a SPA.
- Create: `frontend/src/main.tsx` — bootstrap React.
- Create: `frontend/src/router.tsx` — roteador tipado com a rota principal.
- Create: `frontend/src/app.tsx` — composição da tela principal com gate de autenticação.
- Create: `frontend/src/lib/runtime-config.ts` — leitura segura de `window.__SUPABASE_URL__` e `window.__SUPABASE_ANON_KEY__`.
- Create: `frontend/src/lib/supabase.ts` — criação centralizada do client Supabase.
- Create: `frontend/src/components/auth/login-screen.tsx` — formulário de email/senha preservando os marcadores atuais.
- Create: `frontend/src/components/ide/ide-shell.tsx` — casca mínima da IDE autenticada.
- Create: `frontend/src/components/ide/monaco-editor-pane.tsx` — wrapper do Monaco editável.
- Create: `frontend/src/styles.css` — layout mínimo da tela.
- Create: `tests/test_monaco_main_route.py` — contrato da issue #10 para Monaco na rota principal.
- Modify: `frontend/index.html` — raiz do app e carregamento de `config.js`.
- Modify: `frontend/config.js` — manter a superfície pública de configuração do Supabase.
- Modify: `frontend/Dockerfile` — instalar deps, gerar `dist` e servir build.
- Modify: `frontend/server.py` — servir arquivos de `dist/`.
- Modify: `tests/test_supabase_login_flow.py` — migrar os checks da UI de HTML estático para fontes React/TS.
- Modify: `README.md` — atualizar instruções do frontend e mencionar Monaco na tela principal.

### Task 1: Travar o contrato de autenticação atual e o novo contrato do Monaco

**Files:**
- Modify: `tests/test_supabase_login_flow.py`
- Create: `tests/test_monaco_main_route.py`

- [ ] **Step 1: Write the failing tests**

Replace the HTML-static assertions in `tests/test_supabase_login_flow.py` with source-based checks for the React app:

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SupabaseLoginUiTest(unittest.TestCase):
    def test_frontend_react_entrypoints_exist(self):
        required = [
            ROOT / "frontend" / "index.html",
            ROOT / "frontend" / "config.js",
            ROOT / "frontend" / "package.json",
            ROOT / "frontend" / "src" / "main.tsx",
            ROOT / "frontend" / "src" / "app.tsx",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_app_source_exposes_login_marker(self):
        content = (ROOT / "frontend" / "src" / "app.tsx").read_text(encoding="utf-8")
        self.assertIn("login-screen", content)


if __name__ == "__main__":
    unittest.main()
```

Create `tests/test_monaco_main_route.py`:

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class MonacoMainRouteTest(unittest.TestCase):
    def test_monaco_component_and_router_files_exist(self):
        required = [
            ROOT / "frontend" / "src" / "router.tsx",
            ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx",
            ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_monaco_editor_is_wired_to_the_main_ide_route(self):
        router = (ROOT / "frontend" / "src" / "router.tsx").read_text(encoding="utf-8")
        shell = (ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx").read_text(encoding="utf-8")
        editor = (ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx").read_text(encoding="utf-8")
        self.assertIn('path: "/"', router)
        self.assertIn("MonacoEditorPane", shell)
        self.assertIn("@monaco-editor/react", editor)
        self.assertIn("defaultLanguage", editor)
        self.assertIn("onChange", editor)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py tests/test_monaco_main_route.py -v`
Expected: FAIL with missing `frontend/package.json`, missing `frontend/src/...`, and missing `tests/test_monaco_main_route.py`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/package.json`:

```json
{
  "name": "simples-editor-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "build": "vite build"
  },
  "dependencies": {
    "@monaco-editor/react": "^4.7.0",
    "@supabase/supabase-js": "^2.49.8",
    "@tanstack/react-router": "^1.121.21",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "typescript": "^5.6.3",
    "vite": "^5.4.10"
  }
}
```

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

Create `frontend/vite.config.ts`:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";


export default defineConfig({
  plugins: [react()],
});
```

Create `frontend/src/main.tsx`:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "@tanstack/react-router";
import { router } from "./router";
import "./styles.css";


ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
```

Create `frontend/src/router.tsx`:

```tsx
import { Outlet, createRootRoute, createRoute, createRouter } from "@tanstack/react-router";
import { App } from "./app";


const rootRoute = createRootRoute({
  component: Outlet,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: App,
});

const routeTree = rootRoute.addChildren([indexRoute]);

export const router = createRouter({ routeTree });
```

Update `frontend/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Simples Editor</title>
    <script src="./config.js"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Create placeholders:

```tsx
// frontend/src/app.tsx
export function App() {
  return <main id="login-screen">loading</main>;
}
```

```tsx
// frontend/src/components/ide/ide-shell.tsx
export function IdeShell() {
  return <section id="ide-shell">placeholder</section>;
}
```

```tsx
// frontend/src/components/ide/monaco-editor-pane.tsx
import Editor from "@monaco-editor/react";


export function MonacoEditorPane() {
  return <Editor defaultLanguage="plaintext" value="" onChange={() => {}} />;
}
```

Create `frontend/src/styles.css`:

```css
body {
  margin: 0;
  font-family: Arial, sans-serif;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py tests/test_monaco_main_route.py -v`
Expected: PASS with the new React-source contract checks

- [ ] **Step 5: Commit**

```bash
git add tests/test_supabase_login_flow.py tests/test_monaco_main_route.py frontend/package.json frontend/tsconfig.json frontend/vite.config.ts frontend/index.html frontend/src/main.tsx frontend/src/router.tsx frontend/src/app.tsx frontend/src/components/ide/ide-shell.tsx frontend/src/components/ide/monaco-editor-pane.tsx frontend/src/styles.css
git commit -m "test: add React and Monaco frontend contracts" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Fazer a base do app carregar Supabase e preservar o gate de login

**Files:**
- Create: `frontend/src/lib/runtime-config.ts`
- Create: `frontend/src/lib/supabase.ts`
- Create: `frontend/src/components/auth/login-screen.tsx`
- Modify: `frontend/src/app.tsx`
- Modify: `frontend/config.js`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_supabase_login_flow.py`:

```python
class SupabaseLoginFlowScriptTest(unittest.TestCase):
    def test_runtime_config_and_client_are_centralized(self):
        config = (ROOT / "frontend" / "src" / "lib" / "runtime-config.ts").read_text(encoding="utf-8")
        supabase = (ROOT / "frontend" / "src" / "lib" / "supabase.ts").read_text(encoding="utf-8")
        self.assertIn("window.__SUPABASE_URL__", config)
        self.assertIn("window.__SUPABASE_ANON_KEY__", config)
        self.assertIn("createClient", supabase)

    def test_login_component_keeps_existing_markers(self):
        content = (ROOT / "frontend" / "src" / "components" / "auth" / "login-screen.tsx").read_text(encoding="utf-8")
        app = (ROOT / "frontend" / "src" / "app.tsx").read_text(encoding="utf-8")
        self.assertIn('id="login-form"', content)
        self.assertIn('type="email"', content)
        self.assertIn('type="password"', content)
        self.assertIn("signInWithPassword", app)
        self.assertIn("getSession", app)
        self.assertIn("ide-shell", app)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py -v`
Expected: FAIL with missing `runtime-config.ts`, `supabase.ts`, and `login-screen.tsx`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/lib/runtime-config.ts`:

```ts
declare global {
  interface Window {
    __SUPABASE_URL__?: string;
    __SUPABASE_ANON_KEY__?: string;
  }
}


export function getRuntimeConfig() {
  return {
    supabaseUrl: window.__SUPABASE_URL__ || "https://example.supabase.co",
    supabaseAnonKey: window.__SUPABASE_ANON_KEY__ || "dev-anon-key",
  };
}
```

Create `frontend/src/lib/supabase.ts`:

```ts
import { createClient } from "@supabase/supabase-js";
import { getRuntimeConfig } from "./runtime-config";


const { supabaseUrl, supabaseAnonKey } = getRuntimeConfig();

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

Create `frontend/src/components/auth/login-screen.tsx`:

```tsx
import type { FormEvent } from "react";


type LoginScreenProps = {
  message: string;
  onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void>;
};


export function LoginScreen({ message, onSubmit }: LoginScreenProps) {
  return (
    <section id="login-screen">
      <h1>Sign in to Simples Editor</h1>
      <form id="login-form" onSubmit={onSubmit}>
        <label>
          Email
          <input type="email" name="email" required />
        </label>
        <label>
          Password
          <input type="password" name="password" required />
        </label>
        <button type="submit">Sign in</button>
      </form>
      <p role="status">{message}</p>
    </section>
  );
}
```

Update `frontend/src/app.tsx`:

```tsx
import { useEffect, useState, type FormEvent } from "react";
import { LoginScreen } from "./components/auth/login-screen";
import { IdeShell } from "./components/ide/ide-shell";
import { supabase } from "./lib/supabase";


export function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setAuthenticated(Boolean(data.session));
    });
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const { error } = await supabase.auth.signInWithPassword({
      email: String(formData.get("email") || ""),
      password: String(formData.get("password") || ""),
    });

    if (error) {
      setMessage(error.message);
      return;
    }

    setMessage("");
    setAuthenticated(true);
  }

  if (!authenticated) {
    return <LoginScreen message={message} onSubmit={handleSubmit} />;
  }

  return <IdeShell />;
}
```

Keep `frontend/config.js` as:

```js
window.__SUPABASE_URL__ = window.__SUPABASE_URL__ || "https://example.supabase.co";
window.__SUPABASE_ANON_KEY__ = window.__SUPABASE_ANON_KEY__ || "dev-anon-key";
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_supabase_login_flow.py -v`
Expected: PASS with login markers preserved through the React source

- [ ] **Step 5: Commit**

```bash
git add tests/test_supabase_login_flow.py frontend/config.js frontend/src/lib/runtime-config.ts frontend/src/lib/supabase.ts frontend/src/components/auth/login-screen.tsx frontend/src/app.tsx
git commit -m "feat: port Supabase login gate to React app" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Entregar a tela principal da IDE com Monaco editável

**Files:**
- Modify: `frontend/src/components/ide/ide-shell.tsx`
- Modify: `frontend/src/components/ide/monaco-editor-pane.tsx`
- Modify: `frontend/src/styles.css`
- Modify: `tests/test_monaco_main_route.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_monaco_main_route.py`:

```python
    def test_ide_shell_exposes_editor_surface_copy(self):
        shell = (ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx").read_text(encoding="utf-8")
        self.assertIn("Editor principal", shell)
        self.assertIn("MonacoEditorPane", shell)

    def test_monaco_editor_uses_editable_simples_starter_code(self):
        editor = (ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx").read_text(encoding="utf-8")
        self.assertIn("programa exemplo", editor)
        self.assertIn("defaultValue", editor)
        self.assertIn("readOnly: false", editor)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_monaco_main_route.py -v`
Expected: FAIL because the placeholder shell and editor do not yet expose the expected copy or Monaco options

- [ ] **Step 3: Write minimal implementation**

Update `frontend/src/components/ide/monaco-editor-pane.tsx`:

```tsx
import { useState } from "react";
import Editor from "@monaco-editor/react";


const STARTER_CODE = `programa exemplo
inicio
  escreval("Olá, mundo!")
fim`;


export function MonacoEditorPane() {
  const [code, setCode] = useState(STARTER_CODE);

  return (
    <div className="editor-pane">
      <Editor
        height="70vh"
        defaultLanguage="plaintext"
        defaultValue={STARTER_CODE}
        value={code}
        onChange={(value) => setCode(value || "")}
        options={{
          minimap: { enabled: false },
          fontSize: 15,
          readOnly: false,
          automaticLayout: true,
        }}
      />
    </div>
  );
}
```

Update `frontend/src/components/ide/ide-shell.tsx`:

```tsx
import { MonacoEditorPane } from "./monaco-editor-pane";


export function IdeShell() {
  return (
    <section id="ide-shell" className="ide-shell">
      <header className="ide-header">
        <h2>Editor principal</h2>
        <p>Monaco carregado na rota principal da IDE.</p>
      </header>
      <MonacoEditorPane />
    </section>
  );
}
```

Update `frontend/src/styles.css`:

```css
body {
  margin: 0;
  background: #0f172a;
  color: #e2e8f0;
  font-family: Inter, Arial, sans-serif;
}

#root {
  min-height: 100vh;
}

.ide-shell {
  padding: 24px;
}

.ide-header {
  margin-bottom: 16px;
}

.editor-pane {
  border: 1px solid #334155;
  border-radius: 12px;
  overflow: hidden;
}
```

- [ ] **Step 4: Run tests and build to verify they pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_monaco_main_route.py tests/test_supabase_login_flow.py -v && cd frontend && npm install && npm run build`
Expected: Python tests PASS, `npm install` creates `package-lock.json`, and `vite build` finishes with a generated `dist/`

- [ ] **Step 5: Commit**

```bash
git add tests/test_monaco_main_route.py tests/test_supabase_login_flow.py frontend/package.json frontend/package-lock.json frontend/src/components/ide/ide-shell.tsx frontend/src/components/ide/monaco-editor-pane.tsx frontend/src/styles.css
git commit -m "feat: add Monaco editor to main IDE route" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 4: Fazer o container servir o build React e atualizar a documentação

**Files:**
- Modify: `frontend/Dockerfile`
- Modify: `frontend/server.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_monaco_main_route.py`:

```python
    def test_frontend_container_and_readme_reference_vite_build(self):
        dockerfile = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")
        server = (ROOT / "frontend" / "server.py").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("npm install", dockerfile)
        self.assertIn("npm run build", dockerfile)
        self.assertIn("dist", server)
        self.assertIn("Monaco", readme)
        self.assertIn("npm run build", readme)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_monaco_main_route.py -v`
Expected: FAIL because the container and docs still describe the static HTML server

- [ ] **Step 3: Write minimal implementation**

Update `frontend/Dockerfile`:

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY server.py .
COPY --from=build /app/dist ./dist
EXPOSE 8080
CMD ["python3", "server.py"]
```

Update `frontend/server.py`:

```python
"""Static file server for the built frontend app."""

import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


if __name__ == "__main__":
    with ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"Frontend serving on port {PORT}", flush=True)
        httpd.serve_forever()
```

Append to `README.md` in the frontend section:

````md
## Frontend Monaco foundation

The frontend now builds a React + TypeScript app with Monaco on the main IDE route.

Local frontend build:

```bash
cd frontend
npm install
npm run build
```

The Supabase login gate still controls access to the IDE shell, and the authenticated view now renders Monaco as the main editor surface.
````

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_monaco_main_route.py tests/test_supabase_login_flow.py -v && cd frontend && npm run build`
Expected: PASS from Python tests and a successful Vite build

- [ ] **Step 5: Commit**

```bash
git add tests/test_monaco_main_route.py frontend/Dockerfile frontend/server.py README.md
git commit -m "docs: document Monaco frontend foundation" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
