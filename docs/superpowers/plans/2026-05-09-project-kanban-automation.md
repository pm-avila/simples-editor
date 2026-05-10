# Project Kanban Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatizar a integração entre issues/PRs da Sprint 1, o GitHub Project 2 de `pm-avila` e o arquivo `PROGRESS.md`.

**Architecture:** A solução usa dois scripts Python sem dependências externas: um para sincronizar o item da issue no GitHub Project e outro para gerar `PROGRESS.md` a partir do estado real das issues. GitHub Actions disparam esses scripts em eventos de `issues` e `pull_request`, preservando o fluxo `Backlog -> In progress -> In review -> Done` e a convenção de PR contra `dev`.

**Tech Stack:** GitHub Actions, Python 3 padrão, GitHub GraphQL API, GitHub REST API, Markdown

---

### File structure

- Create: `.github/workflows/project-kanban-sync.yml` — aciona sincronização do Project em eventos de issue/PR.
- Create: `.github/workflows/progress-sync.yml` — atualiza `PROGRESS.md` sob demanda e em eventos da Sprint 1.
- Create: `scripts/project_sync.py` — cliente GraphQL e regras de mapeamento de status do Project.
- Create: `scripts/update_progress.py` — cliente REST e renderização estável do progresso da Sprint 1.
- Create: `tests/test_project_sync.py` — testes unitários do mapeamento e payloads do Project.
- Create: `tests/test_update_progress.py` — testes unitários da geração de `PROGRESS.md`.
- Create: `PROGRESS.md` — visão humana do status da Sprint 1.
- Modify: `README.md` — documenta setup das variables/secrets e o fluxo branch/PR.
- Create: `.gitignore` — evita sujeira de execução Python local.

### Task 1: Implementar o núcleo de sincronização do GitHub Project

**Files:**
- Create: `tests/test_project_sync.py`
- Create: `scripts/project_sync.py`
- Create: `.gitignore`

- [ ] **Step 1: Write the failing tests**

```python
import unittest

from scripts.project_sync import (
    IssueContext,
    PullRequestContext,
    compute_status,
    is_sprint_one_issue,
)


class SprintOneRulesTest(unittest.TestCase):
    def test_accepts_issue_with_sprint_one_milestone(self):
        issue = IssueContext(number=2, state="OPEN", labels=["devops"], milestone="Sprint 1")
        self.assertTrue(is_sprint_one_issue(issue))

    def test_maps_open_issue_without_pr_to_backlog(self):
        issue = IssueContext(number=2, state="OPEN", labels=["sprint-1"], milestone=None)
        self.assertEqual(compute_status(issue, None), "Backlog")

    def test_maps_open_issue_with_draft_pr_to_in_progress(self):
        issue = IssueContext(number=2, state="OPEN", labels=["sprint-1"], milestone=None)
        pr = PullRequestContext(number=12, state="OPEN", is_draft=True)
        self.assertEqual(compute_status(issue, pr), "In progress")

    def test_maps_open_issue_with_ready_pr_to_in_review(self):
        issue = IssueContext(number=2, state="OPEN", labels=["sprint-1"], milestone=None)
        pr = PullRequestContext(number=12, state="OPEN", is_draft=False)
        self.assertEqual(compute_status(issue, pr), "In review")

    def test_maps_closed_issue_to_done(self):
        issue = IssueContext(number=2, state="CLOSED", labels=["sprint-1"], milestone=None)
        self.assertEqual(compute_status(issue, None), "Done")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_project_sync.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing names from `scripts.project_sync`

- [ ] **Step 3: Write minimal implementation**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class IssueContext:
    number: int
    state: str
    labels: list[str]
    milestone: str | None


@dataclass(frozen=True)
class PullRequestContext:
    number: int
    state: str
    is_draft: bool


def is_sprint_one_issue(issue: IssueContext) -> bool:
    return issue.milestone == "Sprint 1" or "sprint-1" in issue.labels


def compute_status(issue: IssueContext, pr: PullRequestContext | None) -> str:
    if issue.state.upper() == "CLOSED":
        return "Done"
    if pr is None or pr.state.upper() != "OPEN":
        return "Backlog"
    if pr.is_draft:
        return "In progress"
    return "In review"
```

Add `.gitignore`:

```gitignore
.env
__pycache__/
tests/__pycache__/
```

- [ ] **Step 4: Expand implementation to support GitHub API orchestration**

Add these units to `scripts/project_sync.py` after tests pass:

```python
import json
import os
import urllib.request


class GitHubProjectSync:
    def __init__(self, token: str, owner: str, project_number: int) -> None:
        self.token = token
        self.owner = owner
        self.project_number = project_number
        self.project_id = self._load_project_id()
        self.status_field_id, self.status_options = self._load_status_field()

    @classmethod
    def from_env(cls) -> "GitHubProjectSync":
        return cls(
            token=os.environ["GITHUB_TOKEN"],
            owner=os.environ["PROJECT_OWNER"],
            project_number=int(os.environ["PROJECT_NUMBER"]),
        )

    def ensure_issue_in_project(self, issue_node_id: str, issue_number: int) -> str:
        existing_item_id = self._find_item_id(issue_number)
        if existing_item_id:
            return existing_item_id
        query = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """
        data = self._graphql(query, {"projectId": self.project_id, "contentId": issue_node_id})
        return data["addProjectV2ItemById"]["item"]["id"]

    def update_status(self, item_id: str, status_name: str) -> None:
        query = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId,
              itemId: $itemId,
              fieldId: $fieldId,
              value: {singleSelectOptionId: $optionId}
            }
          ) {
            projectV2Item { id }
          }
        }
        """
        self._graphql(
            query,
            {
                "projectId": self.project_id,
                "itemId": item_id,
                "fieldId": self.status_field_id,
                "optionId": self.status_options[status_name],
            },
        )
```

```python
def issue_node_id() -> str:
    event = load_event()
    if "issue" in event:
        return event["issue"]["node_id"]
    return event["pull_request"]["closingIssuesReferences"]["nodes"][0]["id"]


def main() -> int:
    issue = load_issue_context()
    pr = load_pull_request_context()
    if not is_sprint_one_issue(issue):
        print(f"Skipping issue #{issue.number}: not Sprint 1")
        return 0
    status = compute_status(issue, pr)
    sync = GitHubProjectSync.from_env()
    item_id = sync.ensure_issue_in_project(issue_node_id=issue_node_id(), issue_number=issue.number)
    sync.update_status(item_id=item_id, status_name=status)
    print(f"Issue #{issue.number} synced to status {status}")
    return 0
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_project_sync.py -v`
Expected: PASS with 5 tests, 0 failures

- [ ] **Step 6: Commit**

```bash
git add .gitignore scripts/project_sync.py tests/test_project_sync.py
git commit -m "feat: add project kanban sync core" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Ligar a automação do Project aos eventos de issue e PR

**Files:**
- Create: `.github/workflows/project-kanban-sync.yml`
- Modify: `scripts/project_sync.py`
- Test: `tests/test_project_sync.py`

- [ ] **Step 1: Add failing tests for event payload parsing**

Append to `tests/test_project_sync.py`:

```python
from scripts.project_sync import extract_issue_number_from_branch, extract_issue_number_from_pr_body


class PullRequestLinkingTest(unittest.TestCase):
    def test_extracts_issue_number_from_feature_branch(self):
        self.assertEqual(extract_issue_number_from_branch("feat/2"), 2)

    def test_extracts_issue_number_from_pr_body(self):
        body = "Implements automation\\n\\nCloses #2"
        self.assertEqual(extract_issue_number_from_pr_body(body), 2)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_project_sync.py -v`
Expected: FAIL with missing helper functions

- [ ] **Step 3: Implement the parsing helpers**

Add to `scripts/project_sync.py`:

```python
import re


def extract_issue_number_from_branch(branch_name: str) -> int | None:
    match = re.fullmatch(r"(?:feat|fix|chore)/(\\d+)", branch_name.strip())
    return int(match.group(1)) if match else None


def extract_issue_number_from_pr_body(body: str | None) -> int | None:
    if not body:
        return None
    match = re.search(r"(?i)(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\\s+#(\\d+)", body)
    return int(match.group(1)) if match else None
```

- [ ] **Step 4: Add the GitHub Actions workflow**

Create `.github/workflows/project-kanban-sync.yml`:

```yaml
name: Project kanban sync

on:
  issues:
    types: [opened, edited, reopened, labeled, unlabeled, closed]
  pull_request:
    types: [opened, edited, reopened, ready_for_review, converted_to_draft, closed]

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: read
      pull-requests: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Sync GitHub Project status
        env:
          GITHUB_TOKEN: ${{ secrets.PROJECT_AUTOMATION_TOKEN }}
          GITHUB_EVENT_PATH: ${{ github.event_path }}
          GITHUB_EVENT_NAME: ${{ github.event_name }}
          PROJECT_OWNER: pm-avila
          PROJECT_NUMBER: "2"
          PROJECT_STATUS_FIELD: Status
        run: python3 scripts/project_sync.py
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_project_sync.py -v`
Expected: PASS with 7 tests, 0 failures

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/project-kanban-sync.yml scripts/project_sync.py tests/test_project_sync.py
git commit -m "feat: automate project kanban updates" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Gerar e manter `PROGRESS.md` a partir das issues reais

**Files:**
- Create: `tests/test_update_progress.py`
- Create: `scripts/update_progress.py`
- Create: `.github/workflows/progress-sync.yml`
- Create: `PROGRESS.md`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from scripts.update_progress import render_progress_markdown


class RenderProgressMarkdownTest(unittest.TestCase):
    def test_renders_open_and_closed_items_for_sprint_one(self):
        issues = [
            {"number": 2, "title": "feat(project): configure delivery kanban workflow", "state": "OPEN"},
            {"number": 1, "title": "feat(repo): bootstrap repository documentation", "state": "CLOSED"},
        ]
        markdown = render_progress_markdown("Sprint 1", issues)
        self.assertIn("- [ ] #2 feat(project): configure delivery kanban workflow", markdown)
        self.assertIn("- [x] #1 feat(repo): bootstrap repository documentation", markdown)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_update_progress.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing `render_progress_markdown`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/update_progress.py`:

```python
def render_progress_markdown(sprint_name: str, issues: list[dict]) -> str:
    lines = ["# Progress", "", f"## {sprint_name}"]
    for issue in sorted(issues, key=lambda item: item["number"]):
        mark = "x" if issue["state"].upper() == "CLOSED" else " "
        lines.append(f"- [{mark}] #{issue['number']} {issue['title']}")
    lines.append("")
    return "\\n".join(lines)
```

- [ ] **Step 4: Expand implementation to fetch Sprint 1 issues and write the file**

Add these units to `scripts/update_progress.py`:

```python
import json
import os
import urllib.request
from pathlib import Path


def fetch_sprint_one_issues(token: str, repo: str) -> list[dict]:
    owner, name = repo.split("/", 1)
    url = (
        f"https://api.github.com/repos/{owner}/{name}/issues"
        "?state=all&milestone=1&labels=sprint-1&per_page=100"
    )
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request) as response:
        payload = json.load(response)
    return [
        {"number": item["number"], "title": item["title"], "state": item["state"].upper()}
        for item in payload
        if "pull_request" not in item
    ]


def main() -> int:
    issues = fetch_sprint_one_issues(token=os.environ["GITHUB_TOKEN"], repo=os.environ["GITHUB_REPOSITORY"])
    content = render_progress_markdown("Sprint 1", issues)
    Path("PROGRESS.md").write_text(content, encoding="utf-8")
    print("Updated PROGRESS.md")
    return 0
```

Create `.github/workflows/progress-sync.yml`:

```yaml
name: Progress sync

on:
  workflow_dispatch:
  issues:
    types: [opened, edited, reopened, labeled, unlabeled, closed]
  pull_request:
    types: [opened, reopened, closed]

jobs:
  progress:
    if: github.event_name == 'workflow_dispatch' || github.ref_name == 'feat/2' || github.base_ref == 'dev'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: read
      pull-requests: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Update progress tracker
        env:
          GITHUB_TOKEN: ${{ github.token }}
          GITHUB_REPOSITORY: ${{ github.repository }}
        run: python3 scripts/update_progress.py
      - name: Commit updated progress
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add PROGRESS.md
          git diff --cached --quiet || git commit -m "docs: refresh sprint 1 progress"
          git push
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_update_progress.py -v`
Expected: PASS with 1 test, 0 failures

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/progress-sync.yml PROGRESS.md scripts/update_progress.py tests/test_update_progress.py
git commit -m "docs: add automated sprint 1 progress tracker" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 4: Documentar configuração e fluxo operacional

**Files:**
- Modify: `README.md`
- Modify: `PROGRESS.md`
- Check: `.github/workflows/project-kanban-sync.yml`
- Check: `.github/workflows/progress-sync.yml`

- [ ] **Step 1: Add a short documentation section to the README**

Append this section to `README.md`:

```md
## Workflow de entrega da Sprint 1

O repositório usa a branch `dev` como base de integração e branches `feat/<issue>` para cada entrega.

Para a automação do GitHub Project funcionar, configure o secret `PROJECT_AUTOMATION_TOKEN` com permissões de `repo` e `project`.

Eventos de issue e pull request sincronizam automaticamente o item correspondente no Project 2 de `pm-avila` com os estados `Backlog`, `In progress`, `In review` e `Done`.

O arquivo `PROGRESS.md` é regenerado a partir das issues da Sprint 1 para manter uma visão resumida do andamento do backlog.
```

- [ ] **Step 2: Review generated progress content**

Run: `cat PROGRESS.md`
Expected: Markdown with `# Progress`, `## Sprint 1` and checklist entries for Sprint 1 issues

- [ ] **Step 3: Run the full local verification**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_project_sync.py tests/test_update_progress.py -v`
Expected: PASS with all tests green

- [ ] **Step 4: Review final diff**

Run: `git --no-pager diff -- README.md .github/workflows/project-kanban-sync.yml .github/workflows/progress-sync.yml scripts/project_sync.py scripts/update_progress.py tests/test_project_sync.py tests/test_update_progress.py PROGRESS.md`
Expected: Diff only for the planned automation files and docs

- [ ] **Step 5: Commit**

```bash
git add README.md PROGRESS.md .github/workflows/project-kanban-sync.yml .github/workflows/progress-sync.yml scripts/project_sync.py scripts/update_progress.py tests/test_project_sync.py tests/test_update_progress.py .gitignore
git commit -m "docs: document sprint 1 delivery workflow" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
