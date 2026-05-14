# Issue #14 — Resizable Editor/NASM Splitter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a draggable vertical splitter between the Monaco editor and the NASM pane, with double-click collapse/restore for the NASM pane.

**Architecture:** Replace the CSS Grid top-row columns with `react-resizable-panels` `PanelGroup`/`Panel`/`PanelResizeHandle` inside `IdeShell`. The NASM `Panel` is `collapsible`; a double-click handler on the resize handle calls the imperative `collapse()`/`expand()` API. The terminal row stays as a CSS fixed-height flex child.

**Tech Stack:** React 18, `react-resizable-panels` v2, TypeScript, Python source-based tests.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `tests/test_ide_splitter.py` | **CREATE** | 6 source-based contract tests for the splitter |
| `frontend/package.json` | **MODIFY** | add `react-resizable-panels` dependency |
| `frontend/src/components/ide/ide-shell.tsx` | **MODIFY** | replace grid top-row with PanelGroup + collapse logic |
| `frontend/src/styles.css` | **MODIFY** | flex-column shell, remove grid columns/rows, add `.resize-handle` |

---

## Worktree setup (run once before starting)

```bash
# From repo root
git worktree add .worktrees/feat-14 -b feat/14
# Verify baseline
cd .worktrees/feat-14
../../.venv/bin/python -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|OK|FAIL)"
# Expected: Ran 241 tests … OK
```

---

## Task 1: Splitter contract tests

**Files:**
- Create: `tests/test_ide_splitter.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ide_splitter.py` with this exact content:

```python
import unittest
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
IDE_SHELL = ROOT / "frontend/src/components/ide/ide-shell.tsx"
STYLES = ROOT / "frontend/src/styles.css"


class IdeShellSplitterTests(unittest.TestCase):

    def test_ide_shell_imports_panel_group(self):
        """IdeShell must import PanelGroup from react-resizable-panels."""
        src = IDE_SHELL.read_text()
        self.assertIn("PanelGroup", src)
        self.assertIn("react-resizable-panels", src)

    def test_ide_shell_imports_panel_resize_handle(self):
        """IdeShell must import PanelResizeHandle from react-resizable-panels."""
        src = IDE_SHELL.read_text()
        self.assertIn("PanelResizeHandle", src)

    def test_nasm_panel_is_collapsible(self):
        """The NASM Panel must have the collapsible attribute."""
        src = IDE_SHELL.read_text()
        self.assertIn("collapsible", src)

    def test_resize_handle_has_double_click(self):
        """PanelResizeHandle must have an onDoubleClick handler."""
        src = IDE_SHELL.read_text()
        self.assertIn("onDoubleClick", src)

    def test_resize_handle_style_in_css(self):
        """styles.css must define .resize-handle rule."""
        css = STYLES.read_text()
        self.assertIn(".resize-handle", css)

    def test_grid_template_columns_removed_from_ide_shell(self):
        """grid-template-columns must be removed from #ide-shell (replaced by PanelGroup)."""
        css = STYLES.read_text()
        self.assertNotIn("grid-template-columns", css)
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd .worktrees/feat-14
../../.venv/bin/python -m unittest tests.test_ide_splitter -v 2>&1
```

Expected: 6 failures (FAIL). If any pass unexpectedly, investigate before continuing.

- [ ] **Step 3: Commit the failing tests**

```bash
git -C .worktrees/feat-14 add tests/test_ide_splitter.py
git -C .worktrees/feat-14 commit -m "test: add splitter contract tests for issue #14"
```

---

## Task 2: Install dependency and implement splitter

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/src/components/ide/ide-shell.tsx`
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Install `react-resizable-panels`**

```bash
cd .worktrees/feat-14/frontend
npm install react-resizable-panels
```

Expected: package added, `package.json` updated with `"react-resizable-panels": "^2.x.x"`, `package-lock.json` updated.

- [ ] **Step 2: Rewrite `ide-shell.tsx`**

Replace the entire contents of `frontend/src/components/ide/ide-shell.tsx` with:

```tsx
import { useRef } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import type { ImperativePanelHandle } from "react-resizable-panels";
import { MonacoEditorPane } from "./monaco-editor-pane";
import { NasmPane } from "./nasm-pane";
import { TerminalPane } from "./terminal-pane";


export function IdeShell() {
  const nasmPanelRef = useRef<ImperativePanelHandle>(null);

  function handleDoubleClick() {
    const panel = nasmPanelRef.current;
    if (!panel) return;
    if (panel.isCollapsed()) {
      panel.expand();
    } else {
      panel.collapse();
    }
  }

  return (
    <div id="ide-shell">
      <PanelGroup direction="horizontal" className="ide-panel-group">
        <Panel defaultSize={60} minSize={30}>
          <div className="editor-area">
            <MonacoEditorPane />
          </div>
        </Panel>
        <PanelResizeHandle className="resize-handle" onDoubleClick={handleDoubleClick} />
        <Panel ref={nasmPanelRef} defaultSize={40} minSize={20} collapsible>
          <NasmPane />
        </Panel>
      </PanelGroup>
      <div className="terminal-area">
        <TerminalPane />
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Update `styles.css`**

Replace the `#ide-shell`, `.editor-area`, `.nasm-pane` (grid-area), and `.terminal-pane` (grid-area) sections so the file reads:

```css
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: sans-serif;
  background: #1e1e1e;
  color: #d4d4d4;
}

#root {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

#ide-shell {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ide-panel-group {
  flex: 1;
  overflow: hidden;
}

.editor-area {
  height: 100%;
  overflow: hidden;
}

.resize-handle {
  width: 4px;
  background: #3c3c3c;
  cursor: col-resize;
  flex-shrink: 0;
  transition: background 0.15s;
}

.resize-handle:hover,
.resize-handle[data-resize-handle-active] {
  background: #007acc;
}

.nasm-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #252526;
  border-left: 1px solid #3c3c3c;
  overflow: hidden;
}

.nasm-pane__header {
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: #858585;
  background: #2d2d2d;
  border-bottom: 1px solid #3c3c3c;
  flex-shrink: 0;
}

.nasm-pane__body {
  flex: 1;
}

.terminal-area {
  height: 200px;
  flex-shrink: 0;
}

.terminal-pane {
  height: 100%;
  background: #1e1e1e;
  border-top: 1px solid #3c3c3c;
  display: flex;
  align-items: center;
  padding: 8px;
  overflow: hidden;
}

.terminal-pane__label {
  font-size: 12px;
  color: #858585;
}
```

- [ ] **Step 4: Run all tests**

```bash
cd .worktrees/feat-14
../../.venv/bin/python -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|OK|FAIL|ERROR)"
```

Expected: `Ran 247 tests … OK` (241 existing + 6 new).

- [ ] **Step 5: Verify TypeScript build**

```bash
cd .worktrees/feat-14/frontend
npm run build 2>&1 | tail -6
```

Expected: `✓ built in …ms` with exit code 0.

- [ ] **Step 6: Commit**

```bash
git -C .worktrees/feat-14 add \
  frontend/package.json \
  frontend/package-lock.json \
  frontend/src/components/ide/ide-shell.tsx \
  frontend/src/styles.css
git -C .worktrees/feat-14 commit -m "feat: add resizable editor/NASM splitter with collapse on double-click (#14)"
```

---

## After all tasks pass review → merge

```bash
# Push and PR
git -C .worktrees/feat-14 push origin feat/14
gh pr create --repo pm-avila/simples-editor --head feat/14 --base dev \
  --title "feat: resizable editor/NASM splitter (issue #14)" \
  --body "Adds react-resizable-panels. Vertical drag handle between editor and NASM. Double-click collapses/restores NASM. Closes #14"

# Merge
gh pr merge <PR_NUMBER> --repo pm-avila/simples-editor --squash --delete-branch

# Cleanup
git worktree remove .worktrees/feat-14 --force
git branch -D feat/14
git checkout dev && git pull --rebase origin dev
```
