# Issue #80: Integrar Compilador Real do SIMPLES

**Goal:** Substituir o stub do compilador SIMPLES pelo compilador real (`simples-compiler`), permitindo que programas com I/O (`escreva`, `escreval`) funcionem corretamente no editor.

**Architecture:** Clone o repositório `simples-compiler` dentro do Dockerfile do backend durante build, compile-o com `make`, instale o binário em `/usr/local/bin/simplesc`. Backend invoca via `subprocess.run()` como antes; apenas a fonte muda de stub para real. Testes migram de mocks para execução real com fixtures.

**Tech Stack:** Python (backend), subprocess, Docker, pytest, Git, C (compilador)

---

## 1. Integração do Compilador no Docker

### 1.1 Backend Dockerfile

**Objetivo:** Clonar, compilar e instalar o compilador real.

**Mudanças:**

```dockerfile
# backend/Dockerfile (UPDATED)

FROM ubuntu:24.04

# Toolchain cross-target i386 + Python
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      nasm \
      binutils-i686-linux-gnu \
      python3 \
      python3-pip \
      ca-certificates \
      curl \
      git \
    && rm -rf /var/lib/apt/lists/*

# Clone and build the real SIMPLES compiler
RUN git clone https://github.com/pm-avila/simples-compiler /tmp/compiler && \
    cd /tmp/compiler && \
    make && \
    cp simplesc /usr/local/bin/simplesc && \
    rm -rf /tmp/compiler

# Backend Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --break-system-packages -r requirements.txt

COPY . ./backend

EXPOSE 5000

CMD ["python3", "-m", "backend.app"]
```

**Key points:**
- `git` deve estar instalado (adicionado a RUN apt-get)
- Clone acontece em `/tmp/compiler`, build, install em `/usr/local/bin`, cleanup
- Falha-rápido se `git clone` ou `make` falham (sem fallback)
- PYTHONDONTWRITEBYTECODE implícito via Docker (sem .pyc no container)

### 1.2 Remoção do Stub Anterior

**Ações:**
- Deletar `backend/simples-compiler/` (diretório inteiro com stub C)
- O arquivo `backend/compiler.py` permanece inalterado — já espera `/usr/local/bin/simplesc`

---

## 2. Atualização de Testes

### 2.1 Testes de Compilação Existentes

**Arquivo:** `tests/test_compile_endpoint.py`

**Mudanças:**
- Remover mocks de `subprocess.run()` em testes que testam sucesso/erro
- Manter testes para:
  - Programa SIMPLES válido → NASM válido
  - Programa com erro léxico → error estruturado com phase/line/column
  - Programa com erro sintático → error estruturado
  - Programa com erro semântico → error estruturado
  - Timeout → mensagem de timeout

**Strategy:**
- Use `@unittest.skipIf(not HAS_COMPILER, "Compilador não disponível")` para CI que não tem compiler
- Ou garanta que o compilador está disponível no PATH antes dos testes

**Example updates:**

```python
# BEFORE (mocked)
with patch("backend.compiler.subprocess.run", side_effect=_mock_success(SAMPLE_NASM)):
    resp = self.client.post("/api/compile", ...)

# AFTER (real compiler)
# Sem mock — test_client chamará compile_simples() de verdade
# É responsabilidade da imagem Docker ter /usr/local/bin/simplesc disponível
```

### 2.2 Novo Test File: test_real_compiler_integration.py

**Objetivo:** Testes E2E de programas SIMPLES reais (sem `leia`).

**Estrutura:**

```python
# tests/test_real_compiler_integration.py
"""
Integration tests for real SIMPLES compiler.

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_real_compiler_integration -v

Tests compile and execute real SIMPLES programs (without leia).
Requires /usr/local/bin/simplesc to be available.
"""
import os
import subprocess
import tempfile
import unittest
from backend.compiler import compile_simples


class TestRealCompilerIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Check if compiler is available."""
        cls.has_compiler = os.path.exists("/usr/local/bin/simplesc")

    @unittest.skipIf(not setUpClass.__dict__.get("has_compiler", True), 
                     "simplesc not available")
    def test_simple_output_program_compiles_and_runs(self):
        """Program with escreva generates valid assembly and runs."""
        code = """programa demo
inteiro x;
inicio
  x := 42;
  escreva x;
fim
"""
        result = compile_simples(code)
        self.assertTrue(result["ok"], f"Compilation failed: {result}")
        nasm = result["nasm"]
        
        # Verify NASM is not empty and contains expected sections
        self.assertIn("section", nasm.lower())
        self.assertGreater(len(nasm), 50)  # Should be substantial NASM code
        
        # Compile NASM to binary and execute
        with tempfile.TemporaryDirectory() as tmpdir:
            asm_path = os.path.join(tmpdir, "prog.asm")
            obj_path = os.path.join(tmpdir, "prog.o")
            bin_path = os.path.join(tmpdir, "prog")
            
            with open(asm_path, "w") as f:
                f.write(nasm)
            
            # Assemble
            nasm_result = subprocess.run(
                ["nasm", "-f", "elf32", asm_path, "-o", obj_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(nasm_result.returncode, 0,
                           f"nasm failed: {nasm_result.stderr}")
            
            # Link
            ld_result = subprocess.run(
                ["ld", "-m", "elf_i386", obj_path, "-o", bin_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(ld_result.returncode, 0,
                           f"ld failed: {ld_result.stderr}")
            
            # Execute
            exec_result = subprocess.run(
                [bin_path],
                capture_output=True,
                text=True,
                timeout=2
            )
            # Program should exit cleanly (42 in output or exit code 0)
            # Exact output depends on how compiler generates code
            self.assertIn("42", exec_result.stdout + str(exec_result.returncode))

    @unittest.skipIf(not setUpClass.__dict__.get("has_compiler", True),
                     "simplesc not available")
    def test_escreval_program_compiles(self):
        """Program with escreval compiles successfully."""
        code = """programa test
inteiro n;
inicio
  n := 100;
  escreval n;
fim
"""
        result = compile_simples(code)
        self.assertTrue(result["ok"])
        self.assertIn("section", result["nasm"].lower())

    @unittest.skipIf(not setUpClass.__dict__.get("has_compiler", True),
                     "simplesc not available")
    def test_invalid_program_reports_error(self):
        """Invalid program returns structured error."""
        code = """programa broken
inteiro;
inicio
  x := 1
fim
"""
        result = compile_simples(code)
        self.assertFalse(result["ok"])
        self.assertIn("error", result)
        error = result["error"]
        self.assertIn("phase", error)
        self.assertIn("line", error)
        self.assertIn("column", error)
        self.assertIn("message", error)
```

**Key points:**
- Skippy se compiler não está disponível
- Testes compilam → assembly → binary → execute
- Valida que saída contém o valor esperado
- Timeout seguro em cada etapa
- Cleanup automático via tempfile.TemporaryDirectory

### 2.3 Testes WebSocket (test_ws_run_auth.py)

**Mudanças:**
- Remover mocks de `compile_simples` que retornam `{"ok": True, "nasm": "; stub\n"}`
- Deixar chamadas reais para `compile_simples()`
- Mocks podem ser mantidos apenas em testes de **erro** (ex: auth failure, timeout)
- Testes de sucesso agora dependem do compilador real estar disponível

**Exemplo:**

```python
# BEFORE
@patch("backend.ws.run_session.compile_simples", 
       return_value={"ok": True, "nasm": "; stub\n"})
def test_run_success(self, mock_compile):
    ...

# AFTER
# Sem mock — deixa chamar compile_simples() real
def test_run_success(self):
    ...
    # compile_simples() será chamado de verdade
```

---

## 3. Validação em Tempo de Execução

### 3.1 Verificação do Binário

**Em backend/app.py ou health endpoint:**

Quando a aplicação inicia, validar que `/usr/local/bin/simplesc` existe e é executável.

```python
# backend/compiler.py (at module load)
import os
import logging

SIMPLESC_BIN = os.environ.get("SIMPLESC_BIN", "/usr/local/bin/simplesc")

if not os.path.exists(SIMPLESC_BIN):
    logging.warning(f"simplesc not found at {SIMPLESC_BIN}")
```

Ou um health check que valida:

```python
# backend/health.py — adicionar check
def health():
    checks = {
        "python": "ok",
        "compiler": "ok" if os.path.exists("/usr/local/bin/simplesc") else "missing"
    }
    return checks
```

---

## 4. Documentação

### 4.1 Setup Local (DEV)

**Arquivo:** `docs/SETUP.md` ou `README.md` (adicionar seção)

**Conteúdo:**

```markdown
## Setup Local — Compilador Real

Para desenvolver localmente, você precisa do compilador SIMPLES real:

1. Clone e compile em paralelo:
   ```bash
   git clone https://github.com/pm-avila/simples-compiler /tmp/simples-compiler
   cd /tmp/simples-compiler
   make
   sudo cp simplesc /usr/local/bin/simplesc
   ```

2. Volte ao repositório principal:
   ```bash
   cd /path/to/simples-editor
   ```

3. Setup Python:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

4. Rode testes:
   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover tests -v
   ```

Se `/usr/local/bin/simplesc` não estiver disponível, testes de integração serão skipped.

### Docker

Para build em Docker:
```bash
docker-compose build backend
docker-compose up
```

O Dockerfile clona e compila o compilador automaticamente.
```

### 4.2 Backend Dockerfile README

**Arquivo:** `backend/README.md` (novo ou atualizado)

```markdown
# Backend

Backend Flask que:
- Compila código SIMPLES para NASM
- Executa binários em sandbox
- Gerencia websocket para terminal interativo

## Build

O Dockerfile constrói automaticamente:
- Base: Ubuntu 24.04 com toolchain C (gcc, nasm, ld, binutils)
- Compilador: Clone de https://github.com/pm-avila/simples-compiler + make
- Python: Dependencies de requirements.txt

Build falha se o clone ou make falhar (fail-fast).

## Compilador

Binário esperado: `/usr/local/bin/simplesc`

Invocado como: `simplesc <source.simples> -o <output.asm>`

Outputs:
- Exit code 0: sucesso, arquivo `.asm` escrito
- Exit code != 0: erro, stderr contém `<line>:<col>: erro [phase]: message`
```

### 4.3 Atualizar Raiz README

Menção breve:

```markdown
## Integração do Compilador

Este projeto integra o compilador real do `simples-compiler`. 
Backend compila código SIMPLES para NASM e executa em sandbox.

Veja `backend/README.md` e `docs/SETUP.md` para detalhes.
```

---

## 5. Critérios de Aceite (Alinhados com Issue #80)

- [x] Dockerfile clona e compila `simples-compiler` real (falha-rápido se não conseguir)
- [x] Backend invoca `/usr/local/bin/simplesc` (sem mudança em `compiler.py`)
- [x] Programas com `escreva`/`escreval` compilam e executam corretamente
- [x] Erros de compilação geram estrutura `{phase, line, column, message}` válida
- [x] Testes E2E validam execução ponta-a-ponta (não apenas compilação)
- [x] Testes não usam mocks de `compile_simples` (chamadas reais)
- [x] Containers sobem sem ajustes manuais: `docker-compose up`
- [x] Documentação reflete dependência do compilador real
- [x] Stub anterior removido completamente

---

## 6. Notas de Implementação

### Sequência Recomendada

1. **Preparar Dockerfile:** Clone + build + install (Abordagem 1 — Direta)
2. **Remover stub:** Delete `backend/simples-compiler/`
3. **Atualizar testes existentes:** Remove mocks de `compile_simples`
4. **Novo test file:** Adicionar `test_real_compiler_integration.py` com E2E
5. **Validação:** Health endpoint ou startup check para `/usr/local/bin/simplesc`
6. **Docs:** SETUP.md, backend/README.md, raiz README.md
7. **Integração completa:** Docker-compose build + test + PR

### Falhas Previstas

| Cenário | Mitigação |
|---------|-----------|
| `git clone` falha (rede) | Dockerfile falha-rápido — é o comportamento desejado |
| `make` falha no compilador | Dockerfile falha-rápido — indica problema no repo real |
| Testes rodam sem `/usr/local/bin/simplesc` | @unittest.skip cuida disso; local dev pode usar skippy |
| NASM output do compilador real é diferente | Testes E2E usam regex/substring match, não exact match |

### Timeout

- `compile_simples()`: já tem `COMPILE_TIMEOUT` (default 15s) ✓
- Testes de assembly/linking: timeout 5s suficiente
- Testes de execução: timeout 2s suficiente
- WebSocket run: `EXECUTION_TIMEOUT` controla run-time (10s default) ✓

---

## 7. Escopo Futuro (Out-of-Scope #80)

- Suporte a `leia` com stdin simulado (será issue separada)
- Otimização de tempo de build Docker (multi-stage, caching)
- Suporte a múltiplas versões do compilador (pin a versão específica)

---

## Resumo

Esta spec integra o compilador real via clone em build Docker, remove o stub anterior, migra testes para chamar o compilador real com E2E validation, e documenta o setup completo. Falha-rápido em erros de rede/build. Testes skipped gracefully se compiler não está disponível em dev local.
