# Issue #17 — Package simplesc in the Backend Image

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Empacotar o binário `simplesc` na imagem Docker do backend para que o pipeline de compilação SIMPLES possa ser invocado pelo serviço Flask.

**Architecture:** Troca a base `python:3.12-slim` por `ubuntu:24.04`, instala `build-essential` + Python, copia `backend/simples-compiler/` para dentro do build context, compila com `make` e instala o binário em `/usr/local/bin/simplesc`. Um stub `simplesc.c` é commitado para que o build funcione em CI sem a implementação real do compilador.

**Tech Stack:** Docker (ubuntu:24.04), C99 (stub simplesc), Make, Python 3 (pip --break-system-packages), Flask

---

## File Map

| Ação | Arquivo |
|---|---|
| Modify | `backend/Dockerfile` |
| Create | `backend/simples-compiler/simplesc.c` |
| Create | `backend/simples-compiler/Makefile` |
| Create | `backend/simples-compiler/README.md` |
| Modify | `tests/test_backend_dockerfile.py` |

---

### Task 1: Criar stub do compilador simplesc

**Files:**
- Create: `backend/simples-compiler/simplesc.c`
- Create: `backend/simples-compiler/Makefile`
- Create: `backend/simples-compiler/README.md`

- [ ] **Step 1: Criar `backend/simples-compiler/simplesc.c`**

```c
/*
 * simplesc stub — placeholder para o compilador SIMPLES real.
 * Uso: simplesc <fonte.simples> -o <saida.asm>
 *
 * Substitua este arquivo pela implementação real do compilador.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *NASM_SKELETON =
    "section .data\n"
    "    msg db 'stub: substitua pelo compilador real', 10\n"
    "    msglen equ $ - msg\n"
    "\n"
    "section .text\n"
    "    global _start\n"
    "_start:\n"
    "    mov eax, 4\n"
    "    mov ebx, 1\n"
    "    mov ecx, msg\n"
    "    mov edx, msglen\n"
    "    int 0x80\n"
    "    mov eax, 1\n"
    "    mov ebx, 0\n"
    "    int 0x80\n";

int main(int argc, char *argv[]) {
    const char *source_file = NULL;
    const char *output_file = NULL;

    /* Parsing de argumentos: simplesc <fonte> -o <saida> */
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            output_file = argv[++i];
        } else if (argv[i][0] != '-') {
            source_file = argv[i];
        }
    }

    if (!source_file || !output_file) {
        fprintf(stderr, "1:1: erro: uso: simplesc <fonte.simples> -o <saida.asm>\n");
        return 1;
    }

    /* Verifica se o arquivo fonte existe */
    FILE *src = fopen(source_file, "r");
    if (!src) {
        fprintf(stderr, "1:1: erro: arquivo nao encontrado: %s\n", source_file);
        return 1;
    }
    fclose(src);

    /* Escreve o skeleton NASM de saida */
    FILE *out = fopen(output_file, "w");
    if (!out) {
        fprintf(stderr, "1:1: erro: nao foi possivel criar: %s\n", output_file);
        return 1;
    }
    fputs(NASM_SKELETON, out);
    fclose(out);

    return 0;
}
```

- [ ] **Step 2: Criar `backend/simples-compiler/Makefile`**

```makefile
CC      = gcc
CFLAGS  = -std=c99 -Wall -Wextra -O2

.PHONY: all clean

all: simplesc

simplesc: simplesc.c
	$(CC) $(CFLAGS) -o simplesc simplesc.c

clean:
	rm -f simplesc
```

- [ ] **Step 3: Criar `backend/simples-compiler/README.md`**

```markdown
# simples-compiler stub

Este diretório contém um **stub** do compilador `simplesc` para uso em CI e
desenvolvimento antes que a implementação real esteja disponível.

## Como substituir

Coloque os fontes reais do compilador aqui e garanta que o `Makefile`
produza um binário chamado `simplesc` na raiz deste diretório.

## Contrato de invocação

```
simplesc <fonte.simples> -o <saida.asm>
```

- Saída 0 + arquivo `.asm` válido em caso de sucesso.
- Saída 1 + mensagem `<linha>:<coluna>: <mensagem>` no stderr em caso de erro.
```

- [ ] **Step 4: Verificar que `make` compila o stub localmente**

```bash
cd backend/simples-compiler && make
./simplesc --help 2>&1 || true
```
Resultado esperado: binário `simplesc` criado sem erros de compilação.

- [ ] **Step 5: Commit**

```bash
git add backend/simples-compiler/
git commit -m "feat(build): add simplesc stub compiler for Docker build

Adiciona stub em C99 com Makefile para que o build da imagem do backend
funcione sem a implementação real do compilador.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Atualizar `backend/Dockerfile` para ubuntu:24.04 com build-essential e simplesc

**Files:**
- Modify: `backend/Dockerfile`

- [ ] **Step 1: Adicionar teste de regressão para a nova base de imagem e presença do simplesc**

Abra `tests/test_backend_dockerfile.py` e adicione a classe ao final do arquivo:

```python
class BackendDockerfileCompilerTest(unittest.TestCase):
    """Dockerfile deve usar ubuntu como base e compilar simplesc."""

    def test_base_image_is_ubuntu(self):
        """FROM deve usar ubuntu (não python:*-slim)."""
        text = _dockerfile_text()
        self.assertIn(
            "ubuntu",
            text,
            "Dockerfile base image must be ubuntu (not python:3.12-slim) "
            "so build-essential is available for compiling simplesc.",
        )

    def test_simplesc_binary_is_installed(self):
        """Dockerfile deve copiar simples-compiler e instalar o binário."""
        text = _dockerfile_text()
        self.assertIn(
            "simples-compiler",
            text,
            "Dockerfile must COPY simples-compiler source tree.",
        )
        self.assertIn(
            "simplesc",
            text,
            "Dockerfile must install simplesc binary (cp simplesc /usr/local/bin/simplesc).",
        )

    def test_build_essential_installed(self):
        """Dockerfile deve instalar build-essential para compilar simplesc."""
        text = _dockerfile_text()
        self.assertIn(
            "build-essential",
            text,
            "Dockerfile must install build-essential to compile the simplesc C source.",
        )
```

- [ ] **Step 2: Executar os novos testes (esperar FALHA)**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_dockerfile.py -v
```

Esperado: 3 novos testes falham com `ubuntu` / `simples-compiler` / `build-essential` não encontrados.

- [ ] **Step 3: Atualizar `backend/Dockerfile`**

Substitua o conteúdo completo do arquivo por:

```dockerfile
# Funciona em x86_64 (dev local) e ARM64 (Oracle Cloud Ampere A1)
FROM ubuntu:24.04

# Toolchain C + Python (sem toolchain i386 — isso fica no issue #18)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      python3 \
      python3-pip \
      ca-certificates \
      curl \
    && rm -rf /var/lib/apt/lists/*

# Compilador SIMPLES
COPY ./simples-compiler /opt/simples-compiler
RUN cd /opt/simples-compiler && make && cp simplesc /usr/local/bin/simplesc

# Backend Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --break-system-packages -r requirements.txt

COPY . ./backend

EXPOSE 5000

CMD ["python3", "-m", "backend.app"]
```

- [ ] **Step 4: Executar todos os testes do Dockerfile (esperar PASS)**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_dockerfile.py -v
```

Esperado: todos os 8 testes passam.

- [ ] **Step 5: Commit**

```bash
git add backend/Dockerfile tests/test_backend_dockerfile.py
git commit -m "feat(build): update backend Dockerfile to ubuntu:24.04 and package simplesc

- Troca base python:3.12-slim por ubuntu:24.04
- Instala build-essential e Python3
- Copia simples-compiler, compila com make, instala em /usr/local/bin/simplesc
- Testes de regressão adicionados para base ubuntu e presença do simplesc

Closes #17

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Self-Review

**Spec coverage:**
- ✅ Imagem compila o `simplesc` (Task 1 + 2: make no Dockerfile)  
- ✅ Binário disponível no runtime (`/usr/local/bin/simplesc`)  
- ✅ Estratégia segue PRD §14.3 (ubuntu:24.04, build-essential, make)

**Placeholder scan:** Nenhum TBD ou TODO.

**Type consistency:** Nenhuma função compartilhada entre tasks.
