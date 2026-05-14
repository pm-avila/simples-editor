# PROGRESS.md Sprint 2 Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the progress generator so `PROGRESS.md` reflects all sprint groups tracked in the repo, then regenerate the file from GitHub issues.

**Architecture:** Keep the existing Python-only generator pattern, but generalize it from a single sprint to multiple sprints. Group issues by sprint number, render one heading per sprint, and keep the output deterministic by sorting both sprint groups and issue numbers.

**Tech Stack:** Python 3 stdlib, GitHub REST API, `unittest`.

---

### Task 1: Generalize the progress generator and tests

**Files:**
- Modify: `scripts/update_progress.py`
- Modify: `tests/test_update_progress.py`

- [ ] **Step 1: Write the failing tests**

Add tests that cover Sprint 2 items rendering under a separate `## Sprint 2` heading and keep Sprint 1 ordering intact:

```python
def test_render_progress_groups_issues_by_sprint():
    issues = [
        {'number': 10, 'title': 'feat(editor): integrate Monaco on the main route', 'state': 'closed', 'labels': [{'name': 'sprint-2'}]},
        {'number': 1, 'title': 'feat(repo): bootstrap repository documentation', 'state': 'closed', 'labels': [{'name': 'sprint-1'}]},
    ]
    md = render_progress(issues)
    assert '## Sprint 1' in md
    assert '## Sprint 2' in md
    assert md.index('## Sprint 1') < md.index('## Sprint 2')
    assert '- [x] #1 feat(repo): bootstrap repository documentation' in md
    assert '- [x] #10 feat(editor): integrate Monaco on the main route' in md
```

Also add a test that labels or milestones for Sprint 2 qualify as sprint issues:

```python
def test_sprint2_label_qualifies():
    issue = {'number': 10, 'title': 'feat(editor): integrate Monaco on the main route', 'state': 'closed', 'labels': [{'name': 'sprint-2'}]}
    assert is_sprint_issue(issue)
```

- [ ] **Step 2: Run the targeted tests to verify they fail**

Run:

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples
python3 -m unittest tests.test_update_progress -v
```

Expected: the new Sprint 2 tests fail before the generator is updated.

- [ ] **Step 3: Implement the minimal generator change**

Update `scripts/update_progress.py` so it:

```python
def sprint_number_for_issue(issue: dict) -> int | None:
    ...

def render_progress(issues: list) -> str:
    grouped = {1: [...], 2: [...]}
    lines = ['# Progress', '']
    for sprint_number in sorted(grouped):
        lines.extend([f'## Sprint {sprint_number}', ''])
        for issue in sorted(grouped[sprint_number], key=lambda i: i['number']):
            box = 'x' if issue.get('state', 'open') == 'closed' else ' '
            lines.append(f"- [{box}] #{issue['number']} {issue['title']}")
        lines.append('')
    return '\n'.join(lines)
```

Keep the GitHub fetch logic unchanged except for using the generalized sprint predicate.

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples
python3 -m unittest tests.test_update_progress -v
```

Expected: all update-progress tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/update_progress.py tests/test_update_progress.py
git commit -m "feat: extend PROGRESS generator to Sprint 2"
```

### Task 2: Regenerate PROGRESS.md

**Files:**
- Modify: `PROGRESS.md`

- [ ] **Step 1: Regenerate the file from GitHub issues**

Run:

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples
GITHUB_TOKEN=$(gh auth token) GITHUB_REPOSITORY=pm-avila/simples-editor python3 scripts/update_progress.py
```

Expected: `PROGRESS.md updated.` and the file contains the sprint sections currently present in the repo.

- [ ] **Step 2: Verify the rendered output**

Run:

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples
git diff -- PROGRESS.md
```

Expected: Sprint 1 through Sprint 6 sections are rendered in order, with closed issues checked and open issues unchecked.

- [ ] **Step 3: Commit**

```bash
git add PROGRESS.md
git commit -m "docs: update PROGRESS.md for Sprint 2"
```
