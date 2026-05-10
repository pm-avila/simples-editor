# simples-editor

## Public health check

The backend exposes `GET /api/health` without JWT for local diagnostics and deployment probes.

Expected healthy response:

    {"status": "ok", "service": "backend"}
