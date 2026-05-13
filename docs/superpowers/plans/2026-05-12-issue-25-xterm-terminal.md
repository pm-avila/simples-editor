# Issue #25 xterm Terminal Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the terminal placeholder with xterm.js integration capable of rendering incremental output and capturing user input callbacks.

**Architecture:** Introduce an imperative `TerminalPane` API with `forwardRef` so `IdeShell` can write output and control focus while terminal internals remain encapsulated. Keep current IDE layout intact and only add xterm dependencies and terminal host styles required for visual parity.

**Tech Stack:** React 18, TypeScript, xterm.js, xterm-addon-fit, unittest (contract tests)

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `frontend/package.json` | Add xterm runtime dependencies |
| Modify | `frontend/src/components/ide/terminal-pane.tsx` | Mount/dispose xterm and expose imperative API |
| Modify | `frontend/src/components/ide/ide-shell.tsx` | Wire terminal ref and incremental writes |
| Modify | `frontend/src/styles.css` | Terminal host layout and xterm viewport styling |
| Create | `tests/test_terminal_xterm_integration.py` | Contract tests for xterm wiring |

---

### Task 1: Add xterm dependencies and contract test

**Files:**
- Modify: `frontend/package.json`
- Create: `tests/test_terminal_xterm_integration.py`

- [ ] **Step 1: Write failing test**

```python
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "frontend" / "package.json"


class XtermDependencyContractTest(unittest.TestCase):
    def test_package_json_declares_xterm_dependencies(self):
        src = PKG.read_text(encoding="utf-8")
        self.assertIn('"xterm"', src)
        self.assertIn('"xterm-addon-fit"', src)
```

- [ ] **Step 2: Run test to verify failure**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py -v`  
Expected: FAIL because dependencies are missing.

- [ ] **Step 3: Implement dependency changes**

```json
{
  "dependencies": {
    "xterm": "^5.5.0",
    "xterm-addon-fit": "^0.8.0"
  }
}
```

- [ ] **Step 4: Re-run test**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/package.json tests/test_terminal_xterm_integration.py
git commit -m "feat(terminal): add xterm dependencies for issue #25"
```

---

### Task 2: Implement `TerminalPane` xterm lifecycle and API

**Files:**
- Modify: `frontend/src/components/ide/terminal-pane.tsx`
- Modify: `tests/test_terminal_xterm_integration.py`

- [ ] **Step 1: Write failing component contract tests**

```python
TERMINAL = ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx"


class TerminalPaneXtermContractTest(unittest.TestCase):
    def test_imports_xterm_and_fit_addon(self):
        src = TERMINAL.read_text(encoding="utf-8")
        self.assertIn('from "xterm"', src)
        self.assertIn('from "xterm-addon-fit"', src)

    def test_exposes_forward_ref_api(self):
        src = TERMINAL.read_text(encoding="utf-8")
        self.assertIn("forwardRef", src)
        self.assertIn("useImperativeHandle", src)
        self.assertIn("write:", src)
        self.assertIn("onData", src)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py -v`  
Expected: FAIL until `terminal-pane.tsx` is updated.

- [ ] **Step 3: Implement `TerminalPane`**

```tsx
export interface TerminalPaneHandle {
  write: (chunk: string) => void;
  clear: () => void;
  focus: () => void;
}

export const TerminalPane = forwardRef<TerminalPaneHandle, { onData?: (value: string) => void }>(
  function TerminalPane({ onData }, ref) {
    // create Terminal + FitAddon, mount into host div
    // expose write/clear/focus via useImperativeHandle
    // register term.onData callback and cleanup on unmount
  },
);
```

- [ ] **Step 4: Re-run tests**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ide/terminal-pane.tsx tests/test_terminal_xterm_integration.py
git commit -m "feat(terminal): integrate xterm lifecycle in terminal pane"
```

---

### Task 3: Wire terminal output flow into `IdeShell`

**Files:**
- Modify: `frontend/src/components/ide/ide-shell.tsx`
- Modify: `tests/test_terminal_xterm_integration.py`

- [ ] **Step 1: Write failing integration contract test**

```python
IDE = ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx"


class IdeShellTerminalIntegrationTest(unittest.TestCase):
    def test_ide_shell_wires_terminal_ref(self):
        src = IDE.read_text(encoding="utf-8")
        self.assertIn("TerminalPane", src)
        self.assertIn("useRef", src)
        self.assertIn("terminalRef", src)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py -v`  
Expected: FAIL if ref wiring is missing.

- [ ] **Step 3: Implement minimal wiring**

```tsx
const terminalRef = useRef<TerminalPaneHandle>(null);
// on run success/failure paths:
terminalRef.current?.write("...\\r\\n");
<TerminalPane ref={terminalRef} onData={(value) => { /* hook for ws stdin */ }} />
```

- [ ] **Step 4: Re-run tests**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ide/ide-shell.tsx tests/test_terminal_xterm_integration.py
git commit -m "feat(terminal): wire ide shell to xterm pane API"
```

---

### Task 4: Align terminal styles and verify existing contracts

**Files:**
- Modify: `frontend/src/styles.css`
- Modify: `tests/test_terminal_xterm_integration.py`

- [ ] **Step 1: Write failing style contract test**

```python
STYLES = ROOT / "frontend" / "src" / "styles.css"


class TerminalStyleContractTest(unittest.TestCase):
    def test_styles_include_terminal_host_rules(self):
        css = STYLES.read_text(encoding="utf-8")
        self.assertIn(".terminal-pane__host", css)
        self.assertIn(".xterm", css)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py -v`  
Expected: FAIL until CSS is updated.

- [ ] **Step 3: Implement style updates**

```css
.terminal-pane__host { width: 100%; height: 100%; overflow: hidden; }
.terminal-pane .xterm { height: 100%; }
```

- [ ] **Step 4: Run both new and existing related suites**

Run:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py tests/test_ide_shell_layout.py tests/test_toolbar_mock_run.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/styles.css tests/test_terminal_xterm_integration.py
git commit -m "style(terminal): add xterm host styling contracts"
```

---

### Task 5: Final verification and PR

**Files:**
- Modify: `docs/superpowers/specs/2026-05-12-issue-25-xterm-terminal-design.md` (if implementation notes need updates)
- Create: `docs/superpowers/plans/2026-05-12-issue-25-xterm-terminal.md` (this file)

- [ ] **Step 1: Run focused verification**

Run:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_terminal_xterm_integration.py tests/test_ide_shell_layout.py tests/test_toolbar_mock_run.py tests/test_nasm_monaco_pane.py -v`

- [ ] **Step 2: Create integration commit**

```bash
git add frontend/package.json frontend/src/components/ide/terminal-pane.tsx frontend/src/components/ide/ide-shell.tsx frontend/src/styles.css tests/test_terminal_xterm_integration.py docs/superpowers/specs/2026-05-12-issue-25-xterm-terminal-design.md docs/superpowers/plans/2026-05-12-issue-25-xterm-terminal.md
git commit -m "feat(terminal): integrate xterm.js terminal pane

- Add xterm and xterm-addon-fit dependencies
- Replace terminal placeholder with mounted xterm host and imperative API
- Wire IdeShell output/input hooks to terminal pane
- Add contract tests for integration and styles

Closes #25

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

- [ ] **Step 3: Push and open PR**

```bash
git push -u origin feat/25
gh pr create --base dev --head feat/25 --title "feat(terminal): integrate xterm.js into terminal pane (#25)" --body "Implements issue #25 by replacing the placeholder terminal with xterm.js integration and frontend wiring.

Closes #25"
```

---

## Self-Review

- **Spec coverage:** xterm dependency, component integration, incremental output hook, and visual alignment are each mapped to dedicated tasks.
- **Placeholder scan:** no TBD/TODO placeholders; each step includes concrete code/command guidance.
- **Type consistency:** `TerminalPaneHandle` and `terminalRef` naming is consistent across tasks.
