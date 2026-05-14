# Design: POST /api/compile Endpoint (Issue #19)

## Problem

O pipeline real de compilação (`simplesc → nasm → ld`) não está exposto via API. O frontend precisa de um endpoint REST para acionar a compilação do código SIMPLES e obter o NASM gerado (ou erro estruturado), validando que a camada de compilação funciona independentemente da complexidade do WebSocket.

## Approach

Criar `backend/compiler.py` com a função `compile_simples(code)` que encapsula a invocação de `simplesc` via `subprocess.run`. Adicionar `POST /api/compile` no `backend/app.py` que chama essa função e retorna JSON com `nasm` (sucesso) ou `error` (falha).

## Architecture

```
backend/
├── app.py           ← adiciona rota POST /api/compile
├── compiler.py      ← novo: compile_simples(code) → dict
└── ...

tests/
└── test_compile_endpoint.py  ← novo: testa endpoint com subprocess mockado
```

### Novo módulo: `backend/compiler.py`

```python
compile_simples(code: str) -> dict
# Retorna {"ok": True, "nasm": "<str>"} ou {"ok": False, "error": {...}}
```

O módulo usa `SIMPLESC_BIN` (env var, default `/usr/local/bin/simplesc`) e `COMPILE_TIMEOUT` (env var, default `15`).

### Rota: `POST /api/compile`

| Campo | Detalhe |
|---|---|
| Request body | `{"code": "<source SIMPLES>"}` |
| 200 OK | `{"nasm": "<conteúdo .asm>"}` |
| 422 Unprocessable | `{"error": {"phase": "compile", "line": N, "column": N, "message": "..."}}` |
| 400 Bad Request | código vazio ou payload inválido |

### Formato de erro

O stub `simplesc` emite `<linha>:<coluna>: erro: <mensagem>` no stderr. O módulo `compiler.py` parseia com regex e produz `{"phase": "compile", "line": N, "column": N, "message": "..."}`. A normalização por fase lexer/parser/semântica é responsabilidade da issue #20.

## Data Flow

```
POST /api/compile  {"code": "..."}
  │
  ▼ compiler.py.compile_simples(code)
    → tempdir/programa.simples
    → subprocess.run(["simplesc", src, "-o", asm], timeout=15)
    → lê asm / parseia stderr
  │
  ▼ app.py
  200 {"nasm": "..."} | 422 {"error": {...}}
```

## Testing

Tests em `tests/test_compile_endpoint.py` usam `unittest.mock.patch` para substituir `subprocess.run` — sem necessidade de `simplesc` instalado localmente. Cobre:
- Sucesso com NASM retornado
- Falha com erro estruturado
- Código vazio → 400
- Timeout → 422 com mensagem de timeout

## Acceptance Criteria Mapping

| Critério | Implementação |
|---|---|
| Endpoint `POST /api/compile` existe | Rota em `app.py` |
| Aceita código fonte SIMPLES | `{"code": "..."}` no body |
| Sucesso → retorna NASM | 200 `{"nasm": "..."}` |
| Falha → erro estruturado | 422 `{"error": {...}}` |
