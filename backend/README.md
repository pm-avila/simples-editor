# Backend

Backend Flask application that:
- Compiles SIMPLES source code to NASM assembly
- Executes compiled binaries in a sandboxed environment
- Manages WebSocket connections for interactive terminal sessions

## Build

The backend is built in a Docker container. The Dockerfile:
- Uses `ubuntu:24.04` base image with C toolchain (gcc, nasm, ld, binutils)
- Clones and compiles the real SIMPLES compiler from https://github.com/pm-avila/simples-compiler
- Installs the `simplesc` binary to `/usr/local/bin/simplesc`
- Sets up Python environment with Flask and dependencies

**Build will fail-fast** if the compiler clone or make fails (no fallback).

## Compiler

The backend expects the SIMPLES compiler binary at `/usr/local/bin/simplesc`.

**Invocation:**
```bash
simplesc <source.simples> -o <output.asm>
```

**Outputs:**
- Exit code 0: Success — output file `.asm` is written
- Exit code != 0: Error — stderr contains structured error: `<line>:<col>: erro [phase]: message`

**Phases:**
- `lexer` — Lexical analysis error
- `parser` — Syntax error
- `semantic` — Semantic analysis error
- `compile` — General compilation error

## Development

See `docs/SETUP.md` for local development setup.

## Testing

Run backend tests:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover tests -v
```

Integration tests require `/usr/local/bin/simplesc` to be available. Tests will skip gracefully if missing.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_real_compiler_integration -v
```
