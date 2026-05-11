# Simples Editor

Editor visual para a linguagem **SIMPLES**: um ambiente web com frontend, backend e nginx orquestrados por Docker Compose.

## Project overview

Simples Editor is a Web IDE for the educational language SIMPLES: an editor with syntax highlighting, a NASM panel, and a terminal to run programs produced by the compilation pipeline (`simplesc -> nasm -> ld`).

The Product Requirements Document (PRD) is the source of truth for features and priorities. In this branch, the PRD is tracked in the repository as [`prd-simples-online.md`](./prd-simples-online.md).

## Estrutura do repositório

```text
.
├── docker-compose.yml      # Orquestração dos serviços
├── .env.example            # Variáveis de ambiente necessárias (copie para .env)
├── nginx/
│   └── default.conf        # Configuração do nginx (proxy reverso único)
├── frontend/               # Servidor HTTP estático (Python)
│   ├── Dockerfile
│   ├── index.html
│   └── server.py
└── backend/                # API Flask
    ├── Dockerfile
    ├── app.py
    └── requirements.txt
```

## Desenvolvimento local

### 1. Copiar as variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas credenciais reais do Supabase, se necessário
```

### 2. Subir o ambiente

```bash
docker compose up --build
```

### 3. Acessar a aplicação

O **nginx** e o único ponto de entrada. Apos o `docker compose up --build`, acesse:

| Recurso | URL |
|---------|-----|
| Frontend | <http://localhost> |
| API | <http://localhost/api/> |

O nginx (porta 80) roteia:
- `/` -> `frontend:8080`
- `/api/` -> `backend:5000` (com remocao do prefixo `/api/`)

Frontend e backend **nao** expoem portas diretamente ao host; todo o trafego externo passa pelo nginx.

### Configuração nginx

O arquivo `nginx/default.conf` e montado como volume no conteiner nginx. Edite-o para ajustar regras de roteamento sem rebuild da imagem nginx.

## Variáveis de ambiente

Todas as variáveis necessárias estão documentadas em `.env.example`. Copie-o para `.env` e preencha os valores reais antes de executar em produção.

| Variável | Descrição |
|----------|-----------|
| `SUPABASE_URL` | URL do projeto Supabase |
| `SUPABASE_ANON_KEY` | Chave anônima pública do Supabase |
| `SUPABASE_JWT_SECRET` | Segredo JWT do Supabase |
| `COMPILE_TIMEOUT` | Tempo limite de compilação (segundos) |
| `EXECUTION_TIMEOUT` | Tempo limite de execução (segundos) |
| `SANDBOX_IMAGE` | Imagem Docker do sandbox de execução |

O `docker-compose.yml` usa `${VAR:-default}` em todas as referências, portanto o ambiente sobe mesmo sem `.env` (com valores de desenvolvimento padrão).

## Supabase auth foundation

Sprint 1 uses Supabase as the identity provider for v1. The authentication model is based on Supabase Auth and its native `auth.users` table. The backend validates JWTs locally with the shared secret (`SUPABASE_JWT_SECRET`), without querying the database on every request.

## Supabase login

Sprint 1 uses Supabase email/password authentication in the frontend before releasing access to the IDE shell.

The frontend login flow depends on:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

Configure those values before loading the login page by defining:

- `window.__SUPABASE_URL__`
- `window.__SUPABASE_ANON_KEY__`

Example:

```html
<script>
  window.__SUPABASE_URL__ = "https://your-project.supabase.co";
  window.__SUPABASE_ANON_KEY__ = "your-anon-key";
</script>
```

The form sends email/password credentials to Supabase and reveals the protected "IDE access granted" shell after a valid session exists.

## Sprint 1 — Progresso

O acompanhamento macro da Sprint 1 está em [`PROGRESS.md`](PROGRESS.md), gerado automaticamente via GitHub Actions.

### Workflow `Sync Sprint 1 Progress`

O arquivo `.github/workflows/progress-sync.yml` regenera `PROGRESS.md` sempre que:

- uma issue for aberta, editada, fechada, reaberta, rotulada, desrotulada, associada ou desassociada de milestone;
- um pull request for aberto, fechado ou reaberto;
- o workflow for disparado manualmente.

Apenas issues da Sprint 1 (milestone `Sprint 1` ou label `sprint-1`) são incluídas. Pull requests são excluídos.

### Convenções de branch e PR

| Convenção | Valor |
|-----------|-------|
| Branch de trabalho | `feat/<número-da-issue>` |
| Base do PR | `dev` |
| Issues elegíveis | milestone `Sprint 1` ou label `sprint-1` |

## Fonte de verdade

Requisitos e decisões de produto: `prd-simples-online.md`.  
Roadmap por sprint: [`SPRINTS.md`](SPRINTS.md).
