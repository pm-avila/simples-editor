# Design: Enable i386 Linking Toolchain in the Backend Container (Issue #18)

## Problem

Gerar binários ELF x86 32-bit a partir do NASM gerado pelo `simplesc` requer toolchain cross-target dentro do backend. Sem `nasm` e `binutils-i686-linux-gnu` na imagem, o pipeline `simplesc → nasm → ld` não pode avançar além da compilação SIMPLES.

## Approach

Estender o `RUN apt-get install` já presente no `backend/Dockerfile` (introduzido na issue #17) para incluir `nasm` e `binutils-i686-linux-gnu`. O linker correto para ELF i386 em qualquer host (x86_64 ou ARM64) é `i686-linux-gnu-ld`, conforme PRD §14.3 e §8.3.

## Architecture

```
backend/Dockerfile
  ├── FROM ubuntu:24.04
  ├── RUN apt-get install ... build-essential nasm binutils-i686-linux-gnu ...
  └── (demais camadas inalteradas)
```

### Toolchain cross-target

| Ferramenta | Pacote | Uso |
|---|---|---|
| `nasm` | `nasm` | `nasm -f elf32 programa.asm -o programa.o` |
| `i686-linux-gnu-ld` | `binutils-i686-linux-gnu` | `i686-linux-gnu-ld -m elf_i386 programa.o -o programa` |

**Nota de invocação** (PRD §14.3): usar `i686-linux-gnu-ld` em vez de `ld` diretamente, para portabilidade em ARM64.

## Testing

Novo teste `test_backend_dockerfile.py::BackendDockerfileToolchainTest`:
- Verifica que `nasm` está presente no Dockerfile
- Verifica que `binutils-i686-linux-gnu` está presente no Dockerfile

## Acceptance Criteria Mapping

| Critério | Implementação |
|---|---|
| Imagem inclui NASM e `binutils-i686-linux-gnu` | `apt-get install nasm binutils-i686-linux-gnu` |
| Processo de link usa `i686-linux-gnu-ld` para `elf_i386` | Documentado no Dockerfile e nos testes |
| Funciona em x86_64 e ARM64 | `binutils-i686-linux-gnu` é cross-target nativo |
