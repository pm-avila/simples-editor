# Sprint-03: Resultados

## Status

✅ **Todas as 7 issues implementadas, revisadas, testadas e mergeadas**

| PR | Issue | Descrição | Status |
|----|-------|-----------|--------|
| **#64** | **#17** | `simplesc` stub compiler + Dockerfile ubuntu:24.04 | ✅ MERGED |
| **#65** | **#18** | `nasm` + `binutils-i686-linux-gnu` para i386 | ✅ MERGED |
| **#66** | **#19** | `POST /api/compile` endpoint (Flask) | ✅ MERGED |
| **#67** | **#20** | Normalização de erros por fase (lexer/parser/semantic) | ✅ MERGED |
| **#68** | **#23** | Timeout safeguards (15s default) | ✅ MERGED |
| **#69** | **#21** | Monaco markers para erros de compilação | ✅ MERGED |
| **#70** | **#22** | NASM panel sync com assembly gerado | ✅ MERGED |

## Testes

### Backend (Python)
- **57 testes passando** ✅
- `test_compile_endpoint.py` — 9 testes (POST /api/compile)
- `test_compiler_phase.py` — 16 testes (normalização de fase)
- `test_compile_timeout.py` — 14 testes (timeout + _parse_timeout)

Executar:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_compile_*.py -v
```

### Frontend (React/TypeScript)
- **TypeScript sem erros** ✅
- `tsc --noEmit` passa

Executar:
```bash
cd frontend && ./node_modules/.bin/tsc --noEmit
```

## Arquitetura

### Backend

```
backend/
├── compiler.py          # compile_simples(code), _parse_compiler_error(), _parse_timeout()
├── app.py              # POST /api/compile
├── simples-compiler/
│   ├── simplesc.c      # Stub compiler (contrato: simplesc <in> -o <out>)
│   ├── Makefile        # Build script
│   └── README.md
└── Dockerfile          # ubuntu:24.04 + build-essential + nasm + binutils-i686-linux-gnu
```

**Fluxo de compilação:**
1. Frontend faz POST `/api/compile` com código SIMPLES
2. Backend escreve código em temp dir
3. Subprocess invoca `simplesc <src.simples> -o <out.asm>`
4. Backend faz parsing de erro (se houver) com phase normalization
5. Retorna `{ok, nasm?, error?}`

**Phase mapping:**
- `lexico`/`lexer` → phase: `"lexer"`
- `sintatico`/`parser` → phase: `"parser"`
- `semantico`/`semantic` → phase: `"semantic"`
- (desconhecido) → phase: `"compile"`

**Timeout safeguards:**
- Padrão: 15 segundos
- Configurável via `COMPILE_TIMEOUT` env var
- Fallback para 15s se inválido

### Frontend

```
frontend/src/
├── lib/
│   └── compile-api.ts           # compileCode(code): Promise<CompileResult>
├── components/ide/
│   ├── ide-shell.tsx            # Orquestra fluxo (RUN button)
│   ├── monaco-editor-pane.tsx   # Editor com forwardRef + setMarkers()
│   ├── nasm-pane.tsx            # Display NASM (placeholder/compiling/result)
│   ├── toolbar.tsx              # IdeStatus export
│   ├── terminal-pane.tsx        # Logs
│   └── nasm-theme.ts
└── vite-env.d.ts                # Tipos para import.meta.env
```

**Fluxo de UI:**
1. Usuário escreve código no MonacoEditorPane
2. Clica RUN → `handleRun()` em IdeShell
3. `compileCode(code)` faz POST /api/compile
4. Se erro → `editor.setMarkers([error])` marca linha/coluna em vermelho
5. Se sucesso → `setNasmContent(nasm)` preenche NasmPane
6. NasmPane mostra:
   - Placeholder: `"; Execute o programa para ver o assembly gerado."`
   - Compilando: `"; Compilando…"`
   - Sucesso: Assembly NASM x32
   - Erro: `"; Erro de compilação:\n; {message}"`

## Validação

### Testes executáveis localmente

```bash
# Backend
cd /repo && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_compile*.py -v

# Frontend
cd /repo/frontend && npm install && ./node_modules/.bin/tsc --noEmit
```

### Para rodar com Docker

```bash
docker-compose up --build
# Acesse: http://localhost
```

## Documentação

- `docs/pr-evidence.md` — Histórico de todos os PRs mergeados
- `docs/pr-workflow.md` — Workflow obrigatório (brainstorm → plan → implement → PR → review → merge → evidence)
- `.gitignore` — Adicionado `backend/simples-compiler/simplesc`
- `anotacoes-aula.md` — Seção 17 com prompts e respostas da sprint

## Próximos passos

Sprint-04 (issues #24–#29):
- Sandbox container para execução segura
- Integração REPL
- Histórico de compilações
- UI para histórico

---

**Criado:** 2026-05-12
**Sprint:** 3
**Issues:** #17, #18, #19, #20, #21, #22, #23
**PRs:** #64, #65, #66, #67, #68, #69, #70
**Status:** ✅ Completa
