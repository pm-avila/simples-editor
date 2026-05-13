# Docker Compose Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a fundação de desenvolvimento local com `docker-compose.yml`, `nginx`, `frontend` e `backend` mínimos para a Sprint 1.

**Architecture:** A solução cria três serviços reais, porém mínimos: `nginx` como único ponto exposto, `frontend` servindo uma página inicial simples e `backend` com uma aplicação Flask pequena. O compose centraliza rede, dependências e variáveis de ambiente para Supabase, timeouts e imagem de sandbox, preparando a issue #4 sem misturar toda a validação operacional nela.

**Tech Stack:** Docker Compose, nginx, Python 3 + Flask, HTML estático, shell, YAML

---

### File structure

- Create: `docker-compose.yml` — topologia principal com `nginx`, `frontend` e `backend`.
- Create: `.env.example` — placeholders de Supabase, timeouts e sandbox.
- Create: `frontend/Dockerfile` — imagem mínima do serviço de frontend.
- Create: `frontend/index.html` — página inicial estática inicial.
- Create: `frontend/server.py` — servidor HTTP mínimo para servir a página estática.
- Create: `backend/Dockerfile` — imagem mínima do serviço backend em Flask.
- Create: `backend/requirements.txt` — dependência explícita do Flask.
- Create: `backend/app.py` — aplicação Flask skeleton.
- Create: `nginx/default.conf` — proxy para frontend e `/api/`.
- Create: `tests/test_compose_foundation.py` — verificação estrutural do compose e arquivos associados.
- Modify: `README.md` — atualizar instruções locais para refletir os arquivos reais adicionados.

### Task 1: Modelar a fundação do compose e das variáveis

**Files:**
- Create: `tests/test_compose_foundation.py`
- Create: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 1: Write the failing test**

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ComposeFoundationStructureTest(unittest.TestCase):
    def test_compose_declares_three_services_and_expected_variables(self):
        compose_path = ROOT / "docker-compose.yml"
        content = compose_path.read_text(encoding="utf-8")
        self.assertIn("services:", content)
        self.assertIn("nginx:", content)
        self.assertIn("frontend:", content)
        self.assertIn("backend:", content)
        self.assertIn("SUPABASE_URL", content)
        self.assertIn("SUPABASE_ANON_KEY", content)
        self.assertIn("SUPABASE_JWT_SECRET", content)
        self.assertIn("COMPILE_TIMEOUT", content)
        self.assertIn("EXECUTION_TIMEOUT", content)
        self.assertIn("SANDBOX_IMAGE", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v`
Expected: FAIL with `FileNotFoundError` for `docker-compose.yml`

- [ ] **Step 3: Write minimal implementation**

Create `docker-compose.yml`:

```yaml
services:
  nginx:
    image: nginx:1.27-alpine
    ports:
      - "80:80"

  frontend:
    image: python:3.12-alpine

  backend:
    image: python:3.12-slim
    environment:
      SUPABASE_URL: ${SUPABASE_URL:-https://example.supabase.co}
      SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY:-dev-anon-key}
      SUPABASE_JWT_SECRET: ${SUPABASE_JWT_SECRET:-dev-jwt-secret}
      COMPILE_TIMEOUT: ${COMPILE_TIMEOUT:-15}
      EXECUTION_TIMEOUT: ${EXECUTION_TIMEOUT:-10}
      SANDBOX_IMAGE: ${SANDBOX_IMAGE:-simples-runner:dev}
```

Create `.env.example`:

```dotenv
SUPABASE_URL=https://example.supabase.co
SUPABASE_ANON_KEY=dev-anon-key
SUPABASE_JWT_SECRET=dev-jwt-secret
COMPILE_TIMEOUT=15
EXECUTION_TIMEOUT=10
SANDBOX_IMAGE=simples-runner:dev
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v`
Expected: PASS with 1 test, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_compose_foundation.py docker-compose.yml .env.example
git commit -m "feat: add compose foundation contract" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Adicionar os esqueletos de frontend, backend e nginx

**Files:**
- Modify: `tests/test_compose_foundation.py`
- Create: `frontend/Dockerfile`
- Create: `frontend/index.html`
- Create: `frontend/server.py`
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/app.py`
- Create: `nginx/default.conf`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_compose_foundation.py`:

```python
class ComposeFoundationServiceFilesTest(unittest.TestCase):
    def test_required_service_files_exist(self):
        expected_files = [
            ROOT / "frontend" / "Dockerfile",
            ROOT / "frontend" / "index.html",
            ROOT / "frontend" / "server.py",
            ROOT / "backend" / "Dockerfile",
            ROOT / "backend" / "requirements.txt",
            ROOT / "backend" / "app.py",
            ROOT / "nginx" / "default.conf",
        ]
        for path in expected_files:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_compose_uses_internal_network_topology(self):
        content = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("depends_on:", content)
        self.assertIn("default.conf", content)
        self.assertIn("frontend:8080", content)
        self.assertIn("backend:5000", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v`
Expected: FAIL with missing frontend/backend/nginx files

- [ ] **Step 3: Write minimal implementation**

Create `frontend/Dockerfile`:

```dockerfile
FROM python:3.12-alpine
WORKDIR /app
COPY index.html server.py ./
EXPOSE 8080
CMD ["python3", "server.py"]
```

Create `frontend/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Simples Editor</title>
  </head>
  <body>
    <main>
      <h1>Simples Editor</h1>
      <p>Frontend skeleton running inside Docker Compose.</p>
    </main>
  </body>
</html>
```

Create `frontend/server.py`:

```python
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)
    server.serve_forever()
```

Create `backend/requirements.txt`:

```text
Flask==3.0.3
```

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
EXPOSE 5000
CMD ["python3", "app.py"]
```

Create `backend/app.py`:

```python
from flask import Flask, jsonify


app = Flask(__name__)


@app.get("/")
def root():
    return jsonify({"service": "backend", "status": "bootstrap"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

Create `nginx/default.conf`:

```nginx
server {
    listen 80;

    location / {
        proxy_pass http://frontend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/ {
        proxy_pass http://backend:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Update `docker-compose.yml`:

```yaml
services:
  nginx:
    image: nginx:1.27-alpine
    depends_on:
      - frontend
      - backend
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro

  frontend:
    build:
      context: ./frontend

  backend:
    build:
      context: ./backend
    environment:
      SUPABASE_URL: ${SUPABASE_URL:-https://example.supabase.co}
      SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY:-dev-anon-key}
      SUPABASE_JWT_SECRET: ${SUPABASE_JWT_SECRET:-dev-jwt-secret}
      COMPILE_TIMEOUT: ${COMPILE_TIMEOUT:-15}
      EXECUTION_TIMEOUT: ${EXECUTION_TIMEOUT:-10}
      SANDBOX_IMAGE: ${SANDBOX_IMAGE:-simples-runner:dev}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v`
Expected: PASS with 3 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml frontend backend nginx tests/test_compose_foundation.py
git commit -m "feat: add compose service skeletons" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Documentar o scaffold real no README

**Files:**
- Modify: `tests/test_compose_foundation.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_compose_foundation.py`:

```python
class ComposeFoundationReadmeTest(unittest.TestCase):
    def test_readme_mentions_real_compose_files(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docker-compose.yml", content)
        self.assertIn(".env.example", content)
        self.assertIn("nginx/default.conf", content)
        self.assertIn("frontend/", content)
        self.assertIn("backend/", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v`
Expected: FAIL because the current README still describes compose as planned-only

- [ ] **Step 3: Write minimal implementation**

Update `README.md` to include:

```md
## Bootstrap repository entry points
- `docker-compose.yml` — local topology for nginx, frontend and backend
- `.env.example` — environment placeholders for auth and runtime settings
- `nginx/default.conf` — reverse proxy configuration
- `frontend/` — frontend container skeleton
- `backend/` — backend container skeleton
```

and replace the local development note with:

```md
## Local development flow (Sprint 1 target)
The repository now includes the initial Docker Compose scaffold for Sprint 1. The expected local path is:
1. Copy `.env.example` to `.env` and adjust values when needed.
2. Run `docker compose up --build`.
3. Use nginx on `http://localhost` as the single local entry point.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v`
Expected: PASS with 4 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_compose_foundation.py
git commit -m "docs: document compose foundation scaffold" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
