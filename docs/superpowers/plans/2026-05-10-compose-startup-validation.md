# Docker Compose Startup Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tornar a branch `feat/4` autocontida com o scaffold do compose e validar que `docker compose up --build` sobe o ambiente e responde em `http://localhost`.

**Architecture:** A implementação incorpora na `feat/4` a fundação criada na `feat/3` e adiciona um teste operacional leve de startup local. O foco é garantir que o compose, os Dockerfiles, o nginx e o fluxo documentado funcionem juntos em ambiente limpo, sem expandir o escopo funcional além do bootstrap da Sprint 1.

**Tech Stack:** Docker Compose, nginx, Python 3 + Flask, HTML estático, shell, unittest

---

### File structure

- Modify: `docker-compose.yml` — traz a topologia funcional do compose para a branch.
- Modify: `.env.example` — mantém placeholders coerentes para subida local.
- Create/Modify: `frontend/Dockerfile`
- Create/Modify: `frontend/index.html`
- Create/Modify: `frontend/server.py`
- Create/Modify: `backend/Dockerfile`
- Create/Modify: `backend/requirements.txt`
- Create/Modify: `backend/app.py`
- Create/Modify: `nginx/default.conf`
- Create: `tests/test_compose_startup.py` — validação estrutural do fluxo operacional e contrato de startup.
- Modify: `README.md` — alinhar instruções com o fluxo real validado.

### Task 1: Trazer a fundação do compose para a branch da issue #4

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `frontend/Dockerfile`
- Create: `frontend/index.html`
- Create: `frontend/server.py`
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/app.py`
- Create: `nginx/default.conf`
- Create: `tests/test_compose_startup.py`

- [ ] **Step 1: Write the failing test**

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ComposeStartupFoundationTest(unittest.TestCase):
    def test_required_startup_files_exist(self):
        required = [
            ROOT / "docker-compose.yml",
            ROOT / ".env.example",
            ROOT / "frontend" / "Dockerfile",
            ROOT / "frontend" / "index.html",
            ROOT / "frontend" / "server.py",
            ROOT / "backend" / "Dockerfile",
            ROOT / "backend" / "requirements.txt",
            ROOT / "backend" / "app.py",
            ROOT / "nginx" / "default.conf",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_startup.py -v`
Expected: FAIL with missing compose/scaffold files on `feat/4`

- [ ] **Step 3: Write minimal implementation**

Create `docker-compose.yml`:

```yaml
version: "3.9"

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - frontend
      - backend

  frontend:
    build:
      context: ./frontend
    expose:
      - "8080"
    environment:
      SUPABASE_URL: ${SUPABASE_URL:-https://example.supabase.co}
      SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY:-dev-anon-key}

  backend:
    build:
      context: ./backend
    expose:
      - "5000"
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
      <p>Docker Compose startup scaffold is running.</p>
    </main>
  </body>
</html>
```

Create `frontend/server.py`:

```python
import http.server
from http.server import ThreadingHTTPServer


PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler


with ThreadingHTTPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
```

Create `backend/requirements.txt`:

```text
flask==3.1.0
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


@app.route("/")
def index():
    return jsonify({"status": "ok"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


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
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://backend:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_startup.py -v`
Expected: PASS with 1 test, 0 failures

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml .env.example frontend backend nginx tests/test_compose_startup.py
git commit -m "feat: add compose startup scaffold" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Validar o contrato operacional do startup local

**Files:**
- Modify: `tests/test_compose_startup.py`
- Modify: `docker-compose.yml`
- Modify: `nginx/default.conf`
- Modify: `backend/app.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_compose_startup.py`:

```python
import re


class ComposeStartupContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        cls.nginx = (ROOT / "nginx" / "default.conf").read_text(encoding="utf-8")
        cls.backend = (ROOT / "backend" / "app.py").read_text(encoding="utf-8")

    def test_nginx_is_single_host_entry_point(self):
        self.assertIn('"80:80"', self.compose)
        self.assertNotRegex(self.compose, r'frontend:.*ports:', re.DOTALL)
        self.assertNotRegex(self.compose, r'backend:.*ports:', re.DOTALL)

    def test_nginx_proxies_root_and_api(self):
        self.assertIn("proxy_pass http://frontend:8080;", self.nginx)
        self.assertIn("proxy_pass http://backend:5000/;", self.nginx)

    def test_backend_root_exists_for_api_proxy(self):
        self.assertIn('@app.route("/")', self.backend)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_startup.py -v`
Expected: FAIL until all startup-contract assertions are present

- [ ] **Step 3: Write minimal implementation**

If any part is missing, make the minimal correction so that:

```yaml
  frontend:
    expose:
      - "8080"

  backend:
    expose:
      - "5000"
```

and:

```nginx
location /api/ {
    proxy_pass http://backend:5000/;
}
```

and:

```python
@app.route("/")
def index():
    return jsonify({"status": "ok"})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_startup.py -v`
Expected: PASS with 4 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_compose_startup.py docker-compose.yml nginx/default.conf backend/app.py
git commit -m "test: lock startup topology contract" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Documentar e validar o fluxo local real

**Files:**
- Modify: `tests/test_compose_startup.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_compose_startup.py`:

```python
class ComposeStartupReadmeTest(unittest.TestCase):
    def test_readme_describes_real_startup_flow(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docker compose up --build", content)
        self.assertIn("http://localhost", content)
        self.assertIn(".env.example", content)
        self.assertIn("nginx", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_startup.py -v`
Expected: FAIL because `README.md` on `feat/4` does not yet describe the real startup flow

- [ ] **Step 3: Write minimal implementation**

Update `README.md` to include:

```md
## Desenvolvimento local

1. Copie `.env.example` para `.env`.
2. Rode `docker compose up --build`.
3. Acesse `http://localhost`.

O nginx é o único ponto de entrada local. O frontend responde em `/` e o backend fica atrás de `/api/`.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_startup.py -v`
Expected: PASS with 5 tests, 0 failures

- [ ] **Step 5: Validate the actual startup flow**

Run: `docker compose up --build -d && sleep 10 && curl -fsS http://localhost && docker compose down`
Expected: HTML response from frontend via nginx, exit code 0, and containers shut down cleanly

- [ ] **Step 6: Commit**

```bash
git add README.md tests/test_compose_startup.py
git commit -m "docs: validate local compose startup flow" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
