# Issue #16 — Read-Only Monaco NASM Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `NasmPane` placeholder body with a read-only Monaco `<Editor>` using `language="asm"`, ready to receive `.asm` content via a `value` prop.

**Architecture:** Update `nasm-pane.tsx` to import `Editor` from `@monaco-editor/react` and render it inside `.nasm-pane__body`. The mock message from issue #15 is preserved as a Monaco value when `status === "compiling"`. No new files; no CSS changes needed.

**Tech Stack:** React 18, `@monaco-editor/react` v4 (already installed), TypeScript, Python source-based tests.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `tests/test_nasm_monaco_pane.py` | **CREATE** | 5 source-based contract tests |
| `frontend/src/components/ide/nasm-pane.tsx` | **MODIFY** | Replace body with Monaco read-only editor |

---

## Worktree setup

```bash
# From repo root
git worktree add .worktrees/feat-16 -b feat/16
cd .worktrees/feat-16
../../.venv/bin/python -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|OK|FAIL)"
# Expected: Ran 257 tests … OK
```

---

## Task 1: Contract tests

**Files:**
- Create: `tests/test_nasm_monaco_pane.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_nasm_monaco_pane.py`:

```python
import unittest
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
NASM_PANE = ROOT / "frontend/src/components/ide/nasm-pane.tsx"


class NasmMonacoPaneTests(unittest.TestCase):

    def test_nasm_pane_imports_monaco_editor(self):
        """nasm-pane.tsx must import Editor from @monaco-editor/react."""
        src = NASM_PANE.read_text()
        self.assertIn("@monaco-editor/react", src)
        self.assertIn("Editor", src)

    def test_nasm_pane_uses_asm_language(self):
        """nasm-pane.tsx must set language to asm."""
        src = NASM_PANE.read_text()
        self.assertIn('language="asm"', src)

    def test_nasm_pane_is_readonly(self):
        """nasm-pane.tsx Monaco options must set readOnly: true."""
        src = NASM_PANE.read_text()
        self.assertIn("readOnly: true", src)

    def test_nasm_pane_accepts_value_prop(self):
        """nasm-pane.tsx must declare a value prop in the props interface."""
        src = NASM_PANE.read_text()
        self.assertIn("value?:", src)

    def test_nasm_pane_mock_message_in_monaco(self):
        """nasm-pane.tsx must pass 'compilando' text as Monaco value when compiling."""
        src = NASM_PANE.read_text()
        self.assertIn("compilando", src)
```

- [ ] **Step 2: Run to verify failures**

```bash
cd .worktrees/feat-16
../../.venv/bin/python -m unittest tests.test_nasm_monaco_pane -v 2>&1 | tail -10
```

Expected: 5 failures.

- [ ] **Step 3: Commit**

```bash
git -C .worktrees/feat-16 add tests/test_nasm_monaco_pane.py
git -C .worktrees/feat-16 commit -m "test: add NASM Monaco pane contract tests for issue #16"
```

---

## Task 2: Replace NasmPane body with Monaco

**Files:**
- Modify: `frontend/src/components/ide/nasm-pane.tsx`

- [ ] **Step 1: Replace `nasm-pane.tsx` with this content**

```tsx
import Editor from "@monaco-editor/react";
import { SIMPLES_THEME_ID } from "./simples-theme";

type IdeStatus = "idle" | "compiling";

interface NasmPaneProps {
  status?: IdeStatus;
  value?: string;
}

export function NasmPane({ status = "idle", value = "" }: NasmPaneProps) {
  const editorValue =
    status === "compiling" ? "; compilando... (mock)" : value;

  return (
    <aside className="nasm-pane">
      <header className="nasm-pane__header">NASM x32</header>
      <div className="nasm-pane__body">
        <Editor
          height="100%"
          language="asm"
          theme={SIMPLES_THEME_ID}
          value={editorValue}
          options={{ readOnly: true, minimap: { enabled: false } }}
        />
      </div>
    </aside>
  );
}
```

- [ ] **Step 2: Run all tests**

```bash
cd .worktrees/feat-16
../../.venv/bin/python -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|OK|FAIL|ERROR)"
```

Expected: `Ran 262 tests … OK` (257 existing + 5 new).

- [ ] **Step 3: Verify TypeScript build**

```bash
cd .worktrees/feat-16/frontend
npm run build 2>&1 | tail -5
```

Expected: `✓ built in …ms`

- [ ] **Step 4: Commit**

```bash
git -C .worktrees/feat-16 add \
  frontend/src/components/ide/nasm-pane.tsx
git -C .worktrees/feat-16 commit -m "feat: replace NasmPane placeholder with read-only Monaco editor (#16)"
```

---

## After all tasks pass review → merge

```bash
git -C .worktrees/feat-16 push origin feat/16
gh pr create --repo pm-avila/simples-editor --head feat/16 --base dev \
  --title "feat: read-only Monaco panel for NASM output (issue #16)" \
  --body "Replaces NasmPane placeholder with Monaco read-only editor (language=asm). Accepts value prop for future ASM content. Mock compiling message preserved. Closes #16"
gh pr merge <PR_NUMBER> --repo pm-avila/simples-editor --squash --delete-branch
git worktree remove .worktrees/feat-16 --force
git branch -D feat/16
git checkout dev && git pull --rebase origin dev
```
