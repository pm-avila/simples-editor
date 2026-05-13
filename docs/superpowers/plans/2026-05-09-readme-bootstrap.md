# README Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reescrever `README.md` para atender a issue #1 com onboarding inicial do projeto Simples Editor.

**Architecture:** A entrega é centrada em um único arquivo, transformando o README em um hub de onboarding curto e confiável. O conteúdo deve se apoiar no PRD e no estado atual do repositório, deixando explícito o fluxo local pretendido com `docker compose up` sem inventar artefatos inexistentes.

**Tech Stack:** Markdown, GitHub repository docs, PRD interno (`prd-simples-online.md`)

---

### Task 1: Reescrever o README inicial

**Files:**
- Modify: `README.md`
- Reference: `prd-simples-online.md`
- Reference: `SPRINTS.md`
- Reference: `PROGRESS.md`

- [ ] **Step 1: Substituir o conteúdo mínimo atual por uma estrutura de onboarding**

```md
# Simples Editor

Resumo curto do projeto.

## Visão geral
...

## Stack planejada
...

## Estrutura do repositório
...

## Desenvolvimento local
...

## Fonte de verdade
...
```

- [ ] **Step 2: Preencher a seção de visão geral com base no PRD**

```md
## Visão geral

O **Simples Editor** é uma IDE web para a linguagem SIMPLES. A proposta é permitir que o aluno escreva, compile e execute programas diretamente no navegador, com editor, visualização de NASM e terminal interativo.
```

- [ ] **Step 3: Documentar a stack principal sem extrapolar além do PRD**

```md
## Stack planejada

- Frontend web para editor e interface da IDE
- Backend Flask para orquestrar compilação e execução
- Nginx como reverse proxy local
- Supabase para autenticação
- Docker Compose para subir o ambiente de desenvolvimento
```

- [ ] **Step 4: Explicar a estrutura mínima atual do repositório**

```md
## Estrutura do repositório

- `README.md`: ponto de entrada do projeto
- `prd-simples-online.md`: PRD e fonte de verdade
- `SPRINTS.md`: roadmap por sprint
- `PROGRESS.md`: acompanhamento macro das entregas
- `docs/`: documentação de apoio
```

- [ ] **Step 5: Descrever o fluxo local compatível com Docker Compose**

~~~md
## Desenvolvimento local

O fluxo local adotado pelo projeto é baseado em Docker Compose. A meta da Sprint 1 é permitir que qualquer integrante clone o repositório e suba o ambiente com:

```bash
docker compose up
```

Enquanto a infraestrutura base ainda está sendo consolidada, este README registra esse fluxo como convenção de desenvolvimento local.
~~~

- [ ] **Step 6: Referenciar o PRD como fonte de verdade e registrar o status inicial**

```md
## Fonte de verdade

Os requisitos e decisões de produto estão centralizados em `prd-simples-online.md`.

## Status

O repositório está em fase de bootstrap da Sprint 1.
```

- [ ] **Step 7: Verificar que os critérios da issue aparecem no README**

Run: `rg -n "Simples Editor|Stack|Estrutura|docker compose up|prd-simples-online.md" README.md`
Expected: matches for projeto, stack, estrutura, fluxo local e referência ao PRD

- [ ] **Step 8: Revisar o texto final para consistência com o estado atual do repositório**

Run: `git diff -- README.md`
Expected: diff mostrando a reescrita do README sem instruções incompatíveis com os arquivos existentes

- [ ] **Step 9: Commit**

```bash
git add README.md docs/superpowers/specs/2026-05-09-readme-bootstrap-design.md docs/superpowers/plans/2026-05-09-readme-bootstrap.md
git commit -m "docs: bootstrap repository readme" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
