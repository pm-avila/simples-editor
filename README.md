# Simples Editor

IDE web para a linguagem SIMPLES. Permite escrever, compilar e executar programas no navegador com editor, visualização NASM e terminal interativo.

Short onboarding README for the Simples Editor project (bootstrap stage).

## Project overview

Simples Editor is a Web IDE for the educational language SIMPLES: an editor with syntax highlighting, a NASM panel, and a terminal to run programs produced by the compilation pipeline (`simplesc -> nasm -> ld`).

The Product Requirements Document (PRD) is the source of truth for features and priorities. In this branch, the PRD is tracked in the repository as [`prd-simples-online.md`](./prd-simples-online.md).

## Planned stack (Sprint 1 target)

- nginx (reverse proxy, container)
- Frontend: React with Monaco editor
- Backend: Python (Flask) providing REST/WebSocket APIs
- Authentication: Supabase (provisioned separately)
- Execution/build: dedicated Docker images to build/run programs in a sandbox

Note: the above is the planned stack for Sprint 1. Implementation artifacts (compose files, container images, infra) will be added during the sprint.

## Bootstrap repository entry points

This is a short map of the main tracked artifacts relevant to onboarding. It is not a full inventory of the repository.

- README.md — this file (bootstrap onboarding)
- prd-simples-online.md — PRD / source of truth for product decisions
- LICENSE — project license
- .github/ISSUE_TEMPLATE/feature.md — issue template
- .github/pull_request_template.md — PR template

## Sprint 1 — Progresso

O acompanhamento macro da Sprint 1 está em [`PROGRESS.md`](PROGRESS.md), gerado automaticamente via GitHub Actions.

### Workflow `Sync Sprint 1 Progress`

O arquivo `.github/workflows/progress-sync.yml` regenera `PROGRESS.md` sempre que:

- uma issue for aberta, editada, fechada, reaberta, rotulada, desrotulada, associada ou desassociada de milestone;
- um pull request for aberto, fechado ou reaberto;
- o workflow for disparado manualmente.

Apenas issues da Sprint 1 (milestone `Sprint 1` ou label `sprint-1`) são incluídas. Pull requests são excluídos.

### Convenções de branch e PR

| Convenção | Valor |
|-----------|-------|
| Branch de trabalho | `feat/<número-da-issue>` |
| Base do PR | `dev` |
| Issues elegíveis | milestone `Sprint 1` ou label `sprint-1` |

## Fonte de verdade

Requisitos e decisões de produto: `prd-simples-online.md`.  
Roadmap por sprint: [`SPRINTS.md`](SPRINTS.md).

## Local development flow (Sprint 1 target)

The adopted/target local workflow for Sprint 1 is based on Docker Compose. The repository does not yet include the compose file or related infra, so this is the intended Sprint 1 onboarding path rather than a ready-to-run setup:

1. Install Docker and Docker Compose.
2. Run: `docker compose up` to start proxy, frontend and backend containers.
3. Open the UI at http://localhost (or configured port).

## Where to find the PRD

The PRD is the authoritative source for requirements and acceptance criteria. Use [`prd-simples-online.md`](./prd-simples-online.md) in this branch for the current documented scope and acceptance criteria.

## Status

This README is a short bootstrap for onboarding and Sprint 1 planning. It highlights the main onboarding entry points and marks planned artifacts that will be added during Sprint 1.
