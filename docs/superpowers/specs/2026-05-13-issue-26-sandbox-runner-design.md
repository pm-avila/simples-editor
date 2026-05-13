# Issue #26 Design — Sandbox Runner Image

## Context
The execution stage needs a dedicated runtime image that can run generated x86 32-bit binaries in a constrained environment, including cross-architecture hosts.

## Goals
- Provide a dedicated `runner/Dockerfile` for `simples-runner`.
- Use a minimal Debian slim base.
- Install `qemu-user-static` support for x86 32-bit binaries.
- Enforce sandbox defaults with non-root user and isolated workdir.

## Non-goals
- Wiring this image into orchestration/runtime execution flow.
- Security hardening beyond baseline user/workdir isolation.

## Design
1. Add `runner/Dockerfile` based on `debian:bookworm-slim`.
2. Install only runtime packages needed for execution contract:
   - `qemu-user-static`
   - `ca-certificates`
3. Create `sandbox` user and group with fixed UID/GID.
4. Create and own `/sandbox` working directory.
5. Set `USER sandbox` and `WORKDIR /sandbox`.
6. Use a neutral default command suitable for runtime override.

## Validation
Add a dedicated test file validating Dockerfile contract:
- Base image is Debian slim.
- `qemu-user-static` is installed.
- Non-root sandbox user exists and is selected.
- Workdir is `/sandbox`.
