# Design: Package simplesc in the Backend Image (Issue #17)

## Problem

The backend container is currently based on `python:3.12-slim`, which has no C build toolchain. The `simplesc` binary must be compiled from source and available at runtime for the compile pipeline to function. Without it the compile pipeline stays mocked forever.

## Approach

Follow PRD §14.3 exactly: switch the backend base image to `ubuntu:24.04`, install `build-essential` and Python, copy the `simples-compiler` source tree into the build context, compile `simplesc` with `make`, and install it at `/usr/local/bin/simplesc`.

A `backend/simples-compiler/` stub (minimal C stub + Makefile) is committed so the Docker build succeeds in CI and local development. When the real compiler implementation is ready it replaces the stub contents without any Dockerfile changes.

## Architecture

```
backend/
├── Dockerfile                  ← updated: ubuntu:24.04, build-essential, simples-compiler build
├── simples-compiler/
│   ├── Makefile                ← builds ./simplesc from simplesc.c
│   ├── simplesc.c              ← stub compiler (valid NASM skeleton for testing)
│   └── README.md               ← note: replace with real implementation
└── requirements.txt            ← unchanged
```

### Dockerfile changes

| Before | After |
|---|---|
| `FROM python:3.12-slim` | `FROM ubuntu:24.04` |
| — | `RUN apt-get install ... build-essential python3 python3-pip ...` |
| — | `COPY ./simples-compiler /opt/simples-compiler` |
| — | `RUN cd /opt/simples-compiler && make && cp simplesc /usr/local/bin/simplesc` |
| `RUN pip install ...` | `RUN pip install --break-system-packages ...` |
| `CMD ["python3", "-m", "backend.app"]` | unchanged |

### Stub compiler contract

`simplesc <source.simples> -o <output.asm>`  

- Exit 0 on success → writes a minimal valid NASM skeleton to `<output.asm>`.  
- Exit 1 on any error (bad args, file not found) → writes a one-line error to stderr in the format `<line>:<col>: <message>` so the error normaliser (issue #20) can parse it.

## Data Flow

`docker build` → copies `backend/simples-compiler/` → `make` → `simplesc` at `/usr/local/bin/simplesc` → Flask backend can invoke it via `subprocess.run(["simplesc", ...])`.

## Error Handling

- If `simples-compiler/` is missing from the build context, `docker build` fails with a clear `COPY` error — intentional: the dependency is explicit.
- The stub exits with code 1 and writes `1:1: stub compiler — replace with real simplesc` to stderr when the source file is empty/missing.

## Testing

- Existing `test_backend_dockerfile.py` assertions (`COPY . <dest>` and `CMD [..."-m", "backend.app"...]`) remain green.
- New test `test_backend_dockerfile.py::BackendDockerfileCompilerTest` asserts that:
  - The Dockerfile contains `COPY ./simples-compiler` (or `COPY . .` covering it).
  - `/usr/local/bin/simplesc` is placed via a `RUN cp simplesc` step.
  - The base image is `ubuntu` (not `python:3.12-slim`).

## Acceptance Criteria Mapping

| Criterion | Implementation |
|---|---|
| Imagem compila ou incorpora `simplesc` | `make` compila o stub; real compiler replaces stub |
| Binário disponível no runtime | instalado em `/usr/local/bin/simplesc` |
| Estratégia segue PRD §14.3 | Dockerfile segue §14.3 linha a linha |
