# Issue #15 — Mock Compile Toolbar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Toolbar with Run/Stop button that toggles the IDE between `idle` and `compiling` states, wiring read-only editor and NASM mock message without any real backend call.

**Architecture:** New `Toolbar` component owned by `IdeShell`. `IdeShell` holds `useState<"idle" | "compiling">` and passes `status` down to `Toolbar`, `MonacoEditorPane`, and `NasmPane`. `NasmPane` shows "compilando… (mock)" when compiling. `MonacoEditorPane` passes `readOnly` to Monaco `<Editor>`.

**Tech Stack:** React 18, TypeScript, `@monaco-editor/react` v4, Python source-based tests.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `tests/test_toolbar_mock_run.py` | **CREATE** | 9 source-based contract tests |
| `frontend/src/components/ide/toolbar.tsx` | **CREATE** | Run/Stop button component |
| `frontend/src/components/ide/ide-shell.tsx` | **MODIFY** | Add Toolbar + useState for status |
| `frontend/src/components/ide/monaco-editor-pane.tsx` | **MODIFY** | Add `readOnly` prop → Monaco options |
| `frontend/src/components/ide/nasm-pane.tsx` | **MODIFY** | Add `status` prop + mock message |
| `frontend/src/styles.css` | **MODIFY** | Toolbar + mock-msg styles |

---

## Worktree setup (run once before starting)

```bash
# From repo root
git worktree add .worktrees/feat-15 -b feat/15
cd .worktrees/feat-15
../../.venv/bin/python -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|OK|FAIL)"
# Expected: Ran 247 tests … OK
```

---

## Task 1: Contract tests

**Files:**
- Create: `tests/test_toolbar_mock_run.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_toolbar_mock_run.py`:

```python
import unittest
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
TOOLBAR = ROOT / "frontend/src/components/ide/toolbar.tsx"
IDE_SHELL = ROOT / "frontend/src/components/ide/ide-shell.tsx"
MONACO_PANE = ROOT / "frontend/src/components/ide/monaco-editor-pane.tsx"
NASM_PANE = ROOT / "frontend/src/components/ide/nasm-pane.tsx"
STYLES = ROOT / "frontend/src/styles.css"


class ToolbarMockRunTests(unittest.TestCase):

    def test_toolbar_component_exists(self):
        """toolbar.tsx must export a Toolbar function."""
        src = TOOLBAR.read_text()
        self.assertIn("export function Toolbar", src)

    def test_toolbar_has_run_button(self):
        """Toolbar must render the Run button with toolbar__run-btn class."""
        src = TOOLBAR.read_text()
        self.assertIn("toolbar__run-btn", src)

    def test_toolbar_has_stop_button(self):
        """Toolbar must render the Stop button with toolbar__stop-btn class."""
        src = TOOLBAR.read_text()
        self.assertIn("toolbar__stop-btn", src)

    def test_ide_shell_imports_toolbar(self):
        """IdeShell must import Toolbar."""
        src = IDE_SHELL.read_text()
        self.assertIn("Toolbar", src)

    def test_ide_shell_manages_status_state(self):
        """IdeShell must use useState and reference the 'compiling' status."""
        src = IDE_SHELL.read_text()
        self.assertIn("useState", src)
        self.assertIn("compiling", src)

    def test_monaco_pane_accepts_readonly_prop(self):
        """MonacoEditorPane must accept a readOnly prop and pass it to Monaco."""
        src = MONACO_PANE.read_text()
        self.assertIn("readOnly", src)

    def test_nasm_pane_accepts_status_prop(self):
        """NasmPane must accept a status prop."""
        src = NASM_PANE.read_text()
        self.assertIn("status", src)

    def test_nasm_pane_shows_mock_message(self):
        """NasmPane must render a 'compilando' placeholder when compiling."""
        src = NASM_PANE.read_text()
        self.assertIn("compilando", src)

    def test_toolbar_css_exists(self):
        """styles.css must define the .toolbar rule."""
        css = STYLES.read_text()
        self.assertIn(".toolbar", css)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd .worktrees/feat-15
../../.venv/bin/python -m unittest tests.test_toolbar_mock_run -v 2>&1 | tail -14
```

Expected: 9 failures (FAIL).

- [ ] **Step 3: Commit**

```bash
git -C .worktrees/feat-15 add tests/test_toolbar_mock_run.py
git -C .worktrees/feat-15 commit -m "test: add toolbar mock run contract tests for issue #15"
```

---

## Task 2: Implement toolbar and wire state

**Files:**
- Create: `frontend/src/components/ide/toolbar.tsx`
- Modify: `frontend/src/components/ide/ide-shell.tsx`
- Modify: `frontend/src/components/ide/monaco-editor-pane.tsx`
- Modify: `frontend/src/components/ide/nasm-pane.tsx`
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Create `toolbar.tsx`**

Create `frontend/src/components/ide/toolbar.tsx`:

```tsx
type IdeStatus = "idle" | "compiling";

interface ToolbarProps {
  status: IdeStatus;
  onRun: () => void;
  onStop: () => void;
}

export function Toolbar({ status, onRun, onStop }: ToolbarProps) {
  return (
    <header className="toolbar">
      {status === "idle" ? (
        <button className="toolbar__run-btn" onClick={onRun}>
          Run
        </button>
      ) : (
        <button className="toolbar__stop-btn" onClick={onStop}>
          Stop
        </button>
      )}
    </header>
  );
}
```

- [ ] **Step 2: Update `monaco-editor-pane.tsx`**

Replace the file contents with:

```tsx
import Editor from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { registerSimplesLanguage, SIMPLES_LANGUAGE_ID } from "./simples-language";
import { defineSimplesDarkTheme, SIMPLES_THEME_ID } from "./simples-theme";


interface MonacoEditorPaneProps {
  initialValue?: string;
  readOnly?: boolean;
}


export function MonacoEditorPane({ initialValue = "", readOnly = false }: MonacoEditorPaneProps) {
  function onChange(_value: string | undefined) {
    // handle editor content changes
  }

  function beforeMount(monaco: typeof Monaco) {
    registerSimplesLanguage(monaco);
    defineSimplesDarkTheme(monaco);
  }

  return (
    <Editor
      height="100%"
      beforeMount={beforeMount}
      defaultLanguage={SIMPLES_LANGUAGE_ID}
      defaultValue={initialValue}
      theme={SIMPLES_THEME_ID}
      onChange={onChange}
      options={{ readOnly }}
    />
  );
}
```

- [ ] **Step 3: Update `nasm-pane.tsx`**

Replace the file contents with:

```tsx
type IdeStatus = "idle" | "compiling";

interface NasmPaneProps {
  status?: IdeStatus;
}

export function NasmPane({ status = "idle" }: NasmPaneProps) {
  return (
    <aside className="nasm-pane">
      <header className="nasm-pane__header">NASM x32</header>
      <div className="nasm-pane__body">
        {status === "compiling" && (
          <p className="nasm-pane__mock-msg">compilando… (mock)</p>
        )}
      </div>
    </aside>
  );
}
```

- [ ] **Step 4: Update `ide-shell.tsx`**

Replace the file contents with:

```tsx
import { useState, useRef } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import type { ImperativePanelHandle } from "react-resizable-panels";
import { MonacoEditorPane } from "./monaco-editor-pane";
import { NasmPane } from "./nasm-pane";
import { TerminalPane } from "./terminal-pane";
import { Toolbar } from "./toolbar";

type IdeStatus = "idle" | "compiling";


export function IdeShell() {
  const [status, setStatus] = useState<IdeStatus>("idle");
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
      <Toolbar
        status={status}
        onRun={() => setStatus("compiling")}
        onStop={() => setStatus("idle")}
      />
      <PanelGroup direction="horizontal" className="ide-panel-group">
        <Panel defaultSize={60} minSize={30}>
          <div className="editor-area">
            <MonacoEditorPane readOnly={status === "compiling"} />
          </div>
        </Panel>
        <PanelResizeHandle className="resize-handle" onDoubleClick={handleDoubleClick} />
        <Panel ref={nasmPanelRef} defaultSize={40} minSize={20} collapsible>
          <NasmPane status={status} />
        </Panel>
      </PanelGroup>
      <div className="terminal-area">
        <TerminalPane />
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Add toolbar styles to `styles.css`**

Append these rules to the end of `frontend/src/styles.css`:

```css
.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: #2d2d2d;
  border-bottom: 1px solid #3c3c3c;
  flex-shrink: 0;
}

.toolbar__run-btn,
.toolbar__stop-btn {
  padding: 4px 12px;
  font-size: 12px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.toolbar__run-btn {
  background: #0e7a0d;
  color: #fff;
}

.toolbar__stop-btn {
  background: #c72e0f;
  color: #fff;
}

.nasm-pane__mock-msg {
  padding: 8px;
  font-size: 12px;
  color: #858585;
  font-style: italic;
}
```

- [ ] **Step 6: Run all tests**

```bash
cd .worktrees/feat-15
../../.venv/bin/python -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|OK|FAIL|ERROR)"
```

Expected: `Ran 256 tests … OK` (247 existing + 9 new).

- [ ] **Step 7: Verify TypeScript build**

```bash
cd .worktrees/feat-15/frontend
npm run build 2>&1 | tail -5
```

Expected: `✓ built in …ms`

- [ ] **Step 8: Commit**

```bash
git -C .worktrees/feat-15 add \
  frontend/src/components/ide/toolbar.tsx \
  frontend/src/components/ide/ide-shell.tsx \
  frontend/src/components/ide/monaco-editor-pane.tsx \
  frontend/src/components/ide/nasm-pane.tsx \
  frontend/src/styles.css
git -C .worktrees/feat-15 commit -m "feat: add toolbar with mock Run/Stop action (#15)"
```

---

## After all tasks pass review → merge

```bash
git -C .worktrees/feat-15 push origin feat/15
gh pr create --repo pm-avila/simples-editor --head feat/15 --base dev \
  --title "feat: toolbar with mock Run/Stop action (issue #15)" \
  --body "Adds Toolbar component. Run → compiling state (read-only editor, NASM mock msg). Stop → idle. No real backend. Closes #15"
gh pr merge <PR_NUMBER> --repo pm-avila/simples-editor --squash --delete-branch
git worktree remove .worktrees/feat-15 --force
git branch -D feat/15
git checkout dev && git pull --rebase origin dev
```
