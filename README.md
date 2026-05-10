# simples-editor

IDE web para a linguagem SIMPLES. Permite escrever, compilar e executar programas no navegador com editor, visualização NASM e terminal interativo.

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