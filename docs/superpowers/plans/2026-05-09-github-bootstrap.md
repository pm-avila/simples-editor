# GitHub Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar milestones, labels e issues do projeto Simples Editor no GitHub e registrar o acompanhamento inicial em `PROGRESS.md`.

**Architecture:** A implementação usa o `gh` como interface única de automação para o repositório atual, com criação idempotente de milestones e labels e criação em lote das issues aprovadas. O arquivo `PROGRESS.md` é mantido no repositório como visão humana resumida do backlog inicial, separado do GitHub Project e das issues.

**Tech Stack:** GitHub CLI (`gh`), GitHub REST API, Markdown

---

### Task 1: Mapear estado atual do repositório GitHub

**Files:**
- Modify: `docs/superpowers/plans/2026-05-09-github-bootstrap.md`
- Check: `gh repo view`, `gh label list`, `gh api repos/:owner/:repo/milestones`

- [ ] **Step 1: Verificar repositório alvo**

```bash
gh repo view --json nameWithOwner,url
```

- [ ] **Step 2: Verificar labels existentes**

```bash
gh label list --limit 200
```

- [ ] **Step 3: Verificar milestones existentes**

```bash
gh api repos/pm-avila/simples-editor/milestones?state=all
```

- [ ] **Step 4: Verificar issues existentes**

```bash
gh issue list --limit 200 --state all --json number,title
```

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-05-09-github-bootstrap.md
git commit -m "docs: add GitHub bootstrap execution plan"
```

### Task 2: Criar ou atualizar milestones e labels

**Files:**
- Create: none
- Modify: GitHub repository metadata
- Check: `gh api`, `gh label list`

- [ ] **Step 1: Criar milestones Sprint 1 a Sprint 6**

```bash
gh api repos/pm-avila/simples-editor/milestones -f title='Sprint 1'
gh api repos/pm-avila/simples-editor/milestones -f title='Sprint 2'
gh api repos/pm-avila/simples-editor/milestones -f title='Sprint 3'
gh api repos/pm-avila/simples-editor/milestones -f title='Sprint 4'
gh api repos/pm-avila/simples-editor/milestones -f title='Sprint 5'
gh api repos/pm-avila/simples-editor/milestones -f title='Sprint 6'
```

- [ ] **Step 2: Criar ou atualizar labels de sprint**

```bash
gh label create sprint-1 --color B60205 --description 'Issues da Sprint 1' --force
gh label create sprint-2 --color D93F0B --description 'Issues da Sprint 2' --force
gh label create sprint-3 --color FBCA04 --description 'Issues da Sprint 3' --force
gh label create sprint-4 --color 0E8A16 --description 'Issues da Sprint 4' --force
gh label create sprint-5 --color 1D76DB --description 'Issues da Sprint 5' --force
gh label create sprint-6 --color 5319E7 --description 'Issues da Sprint 6' --force
```

- [ ] **Step 3: Criar ou atualizar labels de tipo**

```bash
gh label create frontend --color 2A9D8F --description 'UI, editor, terminal, UX' --force
gh label create backend --color 264653 --description 'API, auth, pipeline, execução' --force
gh label create devops --color 6F42C1 --description 'Compose, Docker, deploy, runtime' --force
gh label create docs --color F4A261 --description 'README, guias, demo, apresentação' --force
gh label create security --color E63946 --description 'Hardening, rate limit, incidentes' --force
```

- [ ] **Step 4: Validar o catálogo final**

```bash
gh label list --limit 200
gh api repos/pm-avila/simples-editor/milestones?state=all
```

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-05-09-github-bootstrap.md
git commit -m "chore: bootstrap labels and milestones"
```

### Task 3: Criar as issues aprovadas

**Files:**
- Create: GitHub issues
- Source: `/Users/avilapm/.copilot/session-state/266d125d-ebc2-486d-ad5a-a7f6eb08e029/plan.md`
- Check: `gh issue list`

- [ ] **Step 1: Preparar lote de issues a partir do plano aprovado**

```bash
python3 - <<'PY'
from pathlib import Path
plan = Path('/Users/avilapm/.copilot/session-state/266d125d-ebc2-486d-ad5a-a7f6eb08e029/plan.md')
assert plan.exists(), plan
print('OK: plano aprovado encontrado')
PY
```

- [ ] **Step 2: Criar cada issue com milestone e labels**

```bash
gh issue create --title 'feat(repo): bootstrap repository documentation' --label sprint-1 --label docs --milestone 'Sprint 1' --body-file /tmp/issue-1.md
gh issue create --title 'feat(project): configure delivery kanban workflow' --label sprint-1 --label devops --milestone 'Sprint 1' --body-file /tmp/issue-2.md
gh issue create --title 'feat(infra): scaffold docker compose foundation' --label sprint-1 --label devops --milestone 'Sprint 1' --body-file /tmp/issue-3.md
```

- [ ] **Step 3: Validar contagem final**

```bash
gh issue list --limit 200 --state all --json number,title,labels,milestone
```

- [ ] **Step 4: Confirmar que as issues ficaram sem assignee**

```bash
gh issue list --limit 200 --state all --json number,title,assignees
```

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-05-09-github-bootstrap.md
git commit -m "chore: bootstrap project issues"
```

### Task 4: Criar `PROGRESS.md`

**Files:**
- Create: `PROGRESS.md`
- Test: `PROGRESS.md`

- [ ] **Step 1: Escrever o arquivo inicial**

```md
# Progress

## Sprint 1
- [ ] feat(repo): bootstrap repository documentation
- [ ] feat(project): configure delivery kanban workflow
```

- [ ] **Step 2: Revisar títulos e agrupamento**

```bash
rg '^## Sprint|^- \[ \]' PROGRESS.md
```

- [ ] **Step 3: Validar consistência com o plano aprovado**

```bash
rg '^#### ' /Users/avilapm/.copilot/session-state/266d125d-ebc2-486d-ad5a-a7f6eb08e029/plan.md | wc -l
rg '^- \[ \]' PROGRESS.md | wc -l
```

- [ ] **Step 4: Revisar `git diff`**

```bash
git --no-pager diff -- PROGRESS.md docs/superpowers/plans/2026-05-09-github-bootstrap.md
```

- [ ] **Step 5: Commit**

```bash
git add PROGRESS.md docs/superpowers/plans/2026-05-09-github-bootstrap.md
git commit -m "docs: add initial project progress tracker"
```
