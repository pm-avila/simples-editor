# PR Workflow Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validar de forma auditavel o fluxo de PR da Sprint 1 com roster versionado, evidência de PR mergeado e documentação do processo de trabalho paralelo.

**Architecture:** A branch `feat/9` vai introduzir documentação pequena e focada em três artefatos: roster do time, fluxo operacional de PR e evidência de PRs mergeados. Como o repositório hoje mostra apenas `pm-avila` como contribuidor, a validação será baseada nesse roster explícito de um integrante e usará o merge real do PR `#48` como prova do fluxo.

**Tech Stack:** Markdown, GitHub CLI, Python 3, unittest

---

### File structure

- Create: `docs/team-roster.md` — fonte de verdade versionada para os integrantes que precisam cumprir o critério da Sprint 1.
- Create: `docs/pr-workflow.md` — fluxo operacional mínimo de branch, review e merge contra `dev`.
- Create: `docs/pr-evidence.md` — registro auditável ligando integrante a PR mergeado.
- Create: `tests/test_pr_workflow_docs.py` — contrato estrutural dos artefatos e da evidência documentada.

### Task 1: Criar os artefatos documentais mínimos do fluxo

**Files:**
- Create: `tests/test_pr_workflow_docs.py`
- Create: `docs/team-roster.md`
- Create: `docs/pr-workflow.md`

- [ ] **Step 1: Write the failing test**

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PrWorkflowDocsFoundationTest(unittest.TestCase):
    def test_required_pr_workflow_files_exist(self):
        required = [
            ROOT / "docs" / "team-roster.md",
            ROOT / "docs" / "pr-workflow.md",
            ROOT / "tests" / "test_pr_workflow_docs.py",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_team_roster_declares_pm_avila(self):
        content = (ROOT / "docs" / "team-roster.md").read_text(encoding="utf-8")
        self.assertIn("pm-avila", content)

    def test_pr_workflow_documents_branch_review_and_merge(self):
        content = (ROOT / "docs" / "pr-workflow.md").read_text(encoding="utf-8")
        self.assertIn("feat/", content)
        self.assertIn("review", content.lower())
        self.assertIn("merge", content.lower())
        self.assertIn("dev", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_pr_workflow_docs.py -v`
Expected: FAIL with missing workflow documentation files on `feat/9`

- [ ] **Step 3: Write minimal implementation**

Create `docs/team-roster.md`:

```md
# Team roster

## Sprint 1 validation scope

The current repository contributor roster used for Sprint 1 PR workflow validation is:

- `pm-avila`
```

Create `docs/pr-workflow.md`:

```md
# Pull request workflow

## Sprint 1 parallel flow

1. Start from `dev`.
2. Create a feature branch named `feat/<issue-number>`.
3. Implement the scoped change on that branch.
4. Open a pull request targeting `dev`.
5. Perform review before merge.
6. Merge the pull request into `dev`.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_pr_workflow_docs.py -v`
Expected: PASS with 3 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_pr_workflow_docs.py docs/team-roster.md docs/pr-workflow.md
git commit -m "docs: add PR workflow validation foundation" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Registrar evidência de PR mergeado por integrante

**Files:**
- Modify: `tests/test_pr_workflow_docs.py`
- Create: `docs/pr-evidence.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_pr_workflow_docs.py`:

```python
class PrWorkflowEvidenceTest(unittest.TestCase):
    def test_pr_evidence_records_merged_pull_request(self):
        content = (ROOT / "docs" / "pr-evidence.md").read_text(encoding="utf-8")
        self.assertIn("pm-avila", content)
        self.assertIn("#48", content)
        self.assertIn("feat/1", content)
        self.assertIn("dev", content)
        self.assertIn("MERGED", content)
```

Keep `if __name__ == "__main__": unittest.main()` at the end of the file after appending the new test class.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_pr_workflow_docs.py -v`
Expected: FAIL because `docs/pr-evidence.md` does not exist yet

- [ ] **Step 3: Perform the real merge validation**

Run:

```bash
GH_PAGER=cat gh pr merge 48 --merge --delete-branch=false
GH_PAGER=cat gh pr view 48 --json number,state,baseRefName,headRefName,url
```

Expected:
- the merge command succeeds;
- PR `#48` is no longer open;
- the follow-up view shows the PR is merged/closed against `dev` from `feat/1`.

- [ ] **Step 4: Write minimal implementation**

Create `docs/pr-evidence.md`:

```md
# Pull request evidence

## Merged PR coverage

| Member | Pull Request | Branch | Base | Status |
| --- | --- | --- | --- | --- |
| `pm-avila` | [#48](https://github.com/pm-avila/simples-editor/pull/48) | `feat/1` | `dev` | `MERGED` |
```

- [ ] **Step 5: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_pr_workflow_docs.py -v`
Expected: PASS with 4 tests, 0 failures

- [ ] **Step 6: Commit**

```bash
git add tests/test_pr_workflow_docs.py docs/pr-evidence.md
git commit -m "docs: record merged PR workflow evidence" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Tornar explícito o alinhamento com a Sprint 1

**Files:**
- Modify: `tests/test_pr_workflow_docs.py`
- Modify: `docs/pr-workflow.md`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_pr_workflow_docs.py`:

```python
class PrWorkflowSprintAlignmentTest(unittest.TestCase):
    def test_pr_workflow_mentions_parallel_sprint_goal(self):
        content = (ROOT / "docs" / "pr-workflow.md").read_text(encoding="utf-8")
        self.assertIn("parallel", content.lower())
        self.assertIn("Sprint 1", content)
        self.assertIn("every team member", content)
```

Keep `if __name__ == "__main__": unittest.main()` at the end of the file after appending the new test class.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_pr_workflow_docs.py -v`
Expected: FAIL because `docs/pr-workflow.md` does not yet describe the Sprint 1 parallel-work goal explicitly

- [ ] **Step 3: Write minimal implementation**

Update `docs/pr-workflow.md` to:

```md
# Pull request workflow

## Sprint 1 parallel flow

This workflow supports Sprint 1 parallel delivery by requiring every team member to ship work through a feature branch and pull request.

1. Start from `dev`.
2. Create a feature branch named `feat/<issue-number>`.
3. Implement the scoped change on that branch.
4. Open a pull request targeting `dev`.
5. Perform review before merge.
6. Merge the pull request into `dev`.
7. Update the PR evidence record after merge.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_pr_workflow_docs.py -v`
Expected: PASS with 5 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
git add tests/test_pr_workflow_docs.py docs/pr-workflow.md
git commit -m "docs: align PR workflow with Sprint 1" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
