# Issue #13 Three-Panel IDE Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar `NasmPane` e `TerminalPane` como placeholders e reestruturar `IdeShell` em layout CSS Grid de três painéis (editor|NASM em cima, terminal em baixo).

**Architecture:** `IdeShell` usa CSS Grid com `grid-template-areas`. Cada painel vive em seu próprio arquivo com responsabilidade única. Estilos no `styles.css` global. Sem splitter redimensionável (issue #14).

**Tech Stack:** React 18, TypeScript 5, Vite, CSS, Python `unittest`

---

### File structure

- Create: `frontend/src/components/ide/nasm-pane.tsx` — placeholder aside com header "NASM x32".
- Create: `frontend/src/components/ide/terminal-pane.tsx` — placeholder section com label "Terminal".
- Modify: `frontend/src/components/ide/ide-shell.tsx` — grid layout com os 3 painéis.
- Modify: `frontend/src/styles.css` — estilos do grid e dos placeholders.
- Create: `tests/test_ide_shell_layout.py` — testes de contrato source-based.

---

### Task 1: Testes de contrato + placeholders NasmPane e TerminalPane

**Files:**
- Create: `tests/test_ide_shell_layout.py`
- Create: `frontend/src/components/ide/nasm-pane.tsx`
- Create: `frontend/src/components/ide/terminal-pane.tsx`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ide_shell_layout.py`:

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class IdePaneContractTest(unittest.TestCase):
    def test_nasm_pane_module_exists(self):
        path = ROOT / "frontend" / "src" / "components" / "ide" / "nasm-pane.tsx"
        self.assertTrue(path.exists(), f"missing: {path}")

    def test_terminal_pane_module_exists(self):
        path = ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx"
        self.assertTrue(path.exists(), f"missing: {path}")

    def test_nasm_pane_has_header(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "nasm-pane.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("NASM x32", content)

    def test_terminal_pane_has_label(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("Terminal", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-13 && ../../.venv/bin/python -m unittest tests/test_ide_shell_layout.py -v
```
Expected: FAIL — both module files do not exist yet.

- [ ] **Step 3: Create `frontend/src/components/ide/nasm-pane.tsx`**

```tsx
export function NasmPane() {
  return (
    <aside className="nasm-pane">
      <header className="nasm-pane__header">NASM x32</header>
      <div className="nasm-pane__body" />
    </aside>
  );
}
```

- [ ] **Step 4: Create `frontend/src/components/ide/terminal-pane.tsx`**

```tsx
export function TerminalPane() {
  return (
    <section className="terminal-pane">
      <span className="terminal-pane__label">Terminal</span>
    </section>
  );
}
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-13 && ../../.venv/bin/python -m unittest tests/test_ide_shell_layout.py -v
```
Expected: 4 tests pass.

- [ ] **Step 6: Commit**

```bash
git -C /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-13 add tests/test_ide_shell_layout.py frontend/src/components/ide/nasm-pane.tsx frontend/src/components/ide/terminal-pane.tsx
git -C /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-13 commit -m "test: add IDE shell layout contract" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Integrar os painéis ao IdeShell com grid layout

**Files:**
- Modify: `frontend/src/components/ide/ide-shell.tsx`
- Modify: `frontend/src/styles.css`
- Modify: `tests/test_ide_shell_layout.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_ide_shell_layout.py` (before `if __name__ == "__main__":`):

```python
class IdeShellIntegrationTest(unittest.TestCase):
    def test_ide_shell_renders_all_three_panes(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("NasmPane", content)
        self.assertIn("TerminalPane", content)
        self.assertIn("MonacoEditorPane", content)

    def test_styles_define_ide_shell_grid(self):
        content = (ROOT / "frontend" / "src" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("#ide-shell", content)
        self.assertIn("grid-template-areas", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-13 && ../../.venv/bin/python -m unittest tests/test_ide_shell_layout.py -v
```
Expected: 4 pass, 2 fail.

- [ ] **Step 3: Replace ENTIRE content of `frontend/src/components/ide/ide-shell.tsx`**

```tsx
import { MonacoEditorPane } from "./monaco-editor-pane";
import { NasmPane } from "./nasm-pane";
import { TerminalPane } from "./terminal-pane";


export function IdeShell() {
  return (
    <div id="ide-shell">
      <div className="editor-area">
        <MonacoEditorPane />
      </div>
      <NasmPane />
      <TerminalPane />
    </div>
  );
}
```

- [ ] **Step 4: Replace ENTIRE content of `frontend/src/styles.css`**

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
  display: grid;
  grid-template-areas:
    "editor nasm"
    "terminal terminal";
  grid-template-columns: 60fr 40fr;
  grid-template-rows: 1fr 200px;
  overflow: hidden;
}

.editor-area {
  grid-area: editor;
  overflow: hidden;
}

.nasm-pane {
  grid-area: nasm;
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

.terminal-pane {
  grid-area: terminal;
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

- [ ] **Step 5: Run tests + build**

Run:
```
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-13 && ../../.venv/bin/python -m unittest tests/test_ide_shell_layout.py tests/test_monaco_main_route.py -v && cd frontend && npm run build
```
Expected: all 6 layout tests + 9 monaco route tests pass, build succeeds.

- [ ] **Step 6: Commit**

```bash
git -C /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-13 add tests/test_ide_shell_layout.py frontend/src/components/ide/ide-shell.tsx frontend/src/styles.css
git -C /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-13 commit -m "feat: build three-panel IDE shell" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
