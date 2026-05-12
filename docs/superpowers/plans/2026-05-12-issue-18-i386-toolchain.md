# Issue #18 — Enable i386 Linking Toolchain in the Backend Container

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Adicionar `nasm` e `binutils-i686-linux-gnu` ao `RUN apt-get install` do `backend/Dockerfile` para viabilizar o pipeline `nasm -f elf32` + `i686-linux-gnu-ld -m elf_i386` em hosts x86_64 e ARM64.

**Architecture:** Extensão mínima do `RUN apt-get install` introduzido na issue #17. Nenhuma outra camada do Dockerfile é alterada.

**Tech Stack:** Docker (ubuntu:24.04), NASM 2.15+, binutils-i686-linux-gnu

---

## File Map

| Ação | Arquivo |
|---|---|
| Modify | `backend/Dockerfile` |
| Modify | `tests/test_backend_dockerfile.py` |

---

### Task 1: Adicionar testes para toolchain i386

**Files:**
- Modify: `tests/test_backend_dockerfile.py`

- [ ] **Step 1: Adicionar `BackendDockerfileToolchainTest` ao final do arquivo de testes**

Abra `tests/test_backend_dockerfile.py` e adicione antes do bloco `if __name__ == "__main__":`:

```python
class BackendDockerfileToolchainTest(unittest.TestCase):
    """Dockerfile deve incluir NASM e binutils-i686-linux-gnu."""

    def test_nasm_installed(self):
        """Dockerfile deve instalar nasm para montar binários ELF i386."""
        text = _dockerfile_text()
        self.assertIn(
            "nasm",
            text,
            "Dockerfile must install nasm to assemble ELF i386 objects "
            "(nasm -f elf32 programa.asm -o programa.o).",
        )

    def test_binutils_i686_installed(self):
        """Dockerfile deve instalar binutils-i686-linux-gnu para linkar ELF i386."""
        text = _dockerfile_text()
        self.assertIn(
            "binutils-i686-linux-gnu",
            text,
            "Dockerfile must install binutils-i686-linux-gnu to provide "
            "i686-linux-gnu-ld for cross-target ELF i386 linking on x86_64 and ARM64.",
        )
```

- [ ] **Step 2: Executar testes (esperar FALHA dos 2 novos)**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_dockerfile.py -v
```

Esperado: `test_binutils_i686_installed` e `test_nasm_installed` falham.

---

### Task 2: Atualizar `backend/Dockerfile` com toolchain i386

**Files:**
- Modify: `backend/Dockerfile`

- [ ] **Step 1: Atualizar o bloco `RUN apt-get install` do Dockerfile**

Substitua o bloco `RUN apt-get update ...` existente por:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      nasm \
      binutils-i686-linux-gnu \
      python3 \
      python3-pip \
      ca-certificates \
      curl \
    && rm -rf /var/lib/apt/lists/*
```

- [ ] **Step 2: Executar todos os testes do Dockerfile (esperar 10/10 PASS)**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_backend_dockerfile.py -v
```

Esperado: 10 testes passam.

- [ ] **Step 3: Commit**

```bash
git add backend/Dockerfile tests/test_backend_dockerfile.py docs/superpowers/specs/2026-05-12-issue-18-i386-toolchain-design.md docs/superpowers/plans/2026-05-12-issue-18-i386-toolchain.md
git commit -m "feat(build): enable i386 linking toolchain in backend container

- Adiciona nasm e binutils-i686-linux-gnu ao apt-get install
- i686-linux-gnu-ld provê link ELF i386 em x86_64 e ARM64
- Testes de regressão adicionados para nasm e binutils-i686-linux-gnu

Closes #18

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Self-Review

**Spec coverage:**
- ✅ Imagem inclui NASM (`nasm` no apt-get)
- ✅ Imagem inclui `binutils-i686-linux-gnu`
- ✅ Funciona em x86_64 e ARM64 (cross-target por design)

**Placeholder scan:** Nenhum TBD.

**Type consistency:** N/A (sem código Python novo).
