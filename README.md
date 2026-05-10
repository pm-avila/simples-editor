# simples-editor

Editor visual para a linguagem **Simples** — ambiente web com compilador, executor de código e integração com Supabase, empacotado via Docker Compose.

---

## Estrutura do repositório

```
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

---

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

O **nginx** é o único ponto de entrada. Após o `docker compose up --build`, acesse:

| Recurso | URL |
|---------|-----|
| Frontend | <http://localhost> |
| API | <http://localhost/api/> |

O nginx (porta 80) roteia:
- `/` → `frontend:8080`
- `/api/` → `backend:5000` (com remoção do prefixo `/api/`)

Frontend e backend **não** expõem portas diretamente ao host — todo o tráfego externo passa pelo nginx.

### Configuração nginx

O arquivo `nginx/default.conf` é montado como volume no contêiner nginx. Edite-o para ajustar regras de roteamento sem rebuild da imagem nginx.

---

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