# Issue #15 — Mock Compile Action from the Toolbar

**Date:** 2026-05-12  
**Issue:** https://github.com/pm-avila/simples-editor/issues/15  
**PRD refs:** §5 RF04, §12.2, §12.3

---

## Problem

The IDE has no toolbar. There is no way to trigger a compile/run action. Even before the real backend is connected, the user should experience the main flow: click Run → see "compiling" visual state → click Stop → return to idle.

---

## Goals

1. Toolbar with a Run/Stop button visible above the IDE panels.
2. Clicking Run transitions the IDE to `compiling` state: editor becomes read-only, NASM pane shows a mock "compilando…" placeholder.
3. Clicking Stop returns to `idle` state: editor becomes editable again, NASM pane clears the placeholder.
4. The mock placeholder clearly communicates that real compilation is not yet active.
5. No real WebSocket / backend call in this issue.

---

## State model

```
type IdeStatus = "idle" | "compiling";
```

Managed with `useState` in `IdeShell`, passed as props to children. Only two states needed for this issue (no `executing`, `compile_error`, `finished` yet — those come with the real backend).

---

## Architecture

### New component: `Toolbar`

```
frontend/src/components/ide/toolbar.tsx
```

- Props: `status: IdeStatus`, `onRun: () => void`, `onStop: () => void`
- Renders a `<header>` with class `toolbar`
- When `status === "idle"`: shows `<button className="toolbar__run-btn">Run</button>` (calls `onRun`)
- When `status === "compiling"`: shows `<button className="toolbar__stop-btn">Stop</button>` (calls `onStop`)

### Updated `IdeShell`

- Owns `[status, setStatus] = useState<IdeStatus>("idle")`
- Renders `<Toolbar>` above the `PanelGroup` inside `#ide-shell`
- Passes `status` down to `MonacoEditorPane` and `NasmPane`
- `onRun` → `setStatus("compiling")`
- `onStop` → `setStatus("idle")`

### Updated `MonacoEditorPane`

- New prop: `readOnly?: boolean` (default `false`)
- Passes `options={{ readOnly }}` to `<Editor>`

### Updated `NasmPane`

- New prop: `status: IdeStatus` (default `"idle"`)
- When `status === "compiling"`: renders `<p className="nasm-pane__mock-msg">compilando… (mock)</p>` inside `.nasm-pane__body`
- When `status === "idle"`: `.nasm-pane__body` is empty (as before)

### Layout in `IdeShell`

```
#ide-shell  (flex-column)
├── Toolbar                         ← NEW (flex-shrink: 0)
├── PanelGroup [horizontal, flex:1]
│   ├── Panel [editor]
│   │   └── MonacoEditorPane readOnly={status === "compiling"}
│   ├── PanelResizeHandle
│   └── Panel [nasm, collapsible]
│       └── NasmPane status={status}
└── .terminal-area (200px)
    └── TerminalPane
```

### CSS additions

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

---

## Files changed

| File | Action |
|---|---|
| `frontend/src/components/ide/toolbar.tsx` | **CREATE** |
| `frontend/src/components/ide/ide-shell.tsx` | **MODIFY** — add Toolbar + state |
| `frontend/src/components/ide/monaco-editor-pane.tsx` | **MODIFY** — add `readOnly` prop |
| `frontend/src/components/ide/nasm-pane.tsx` | **MODIFY** — add `status` prop + mock msg |
| `frontend/src/styles.css` | **MODIFY** — toolbar + mock-msg styles |
| `tests/test_toolbar_mock_run.py` | **CREATE** |

---

## Tests (source-based)

| # | Test | Assertion |
|---|---|---|
| 1 | `test_toolbar_component_exists` | `toolbar.tsx` exports `Toolbar` |
| 2 | `test_toolbar_has_run_button` | `toolbar.tsx` contains `toolbar__run-btn` class |
| 3 | `test_toolbar_has_stop_button` | `toolbar.tsx` contains `toolbar__stop-btn` class |
| 4 | `test_ide_shell_imports_toolbar` | `ide-shell.tsx` imports `Toolbar` |
| 5 | `test_ide_shell_manages_status_state` | `ide-shell.tsx` contains `useState` and `"compiling"` |
| 6 | `test_monaco_pane_accepts_readonly_prop` | `monaco-editor-pane.tsx` contains `readOnly` |
| 7 | `test_nasm_pane_accepts_status_prop` | `nasm-pane.tsx` contains `status` |
| 8 | `test_nasm_pane_shows_mock_message` | `nasm-pane.tsx` contains `compilando` |
| 9 | `test_toolbar_css_exists` | `styles.css` contains `.toolbar` |

---

## Out of scope

- Real WebSocket / backend call (RF04 proper).
- `executing`, `compile_error`, `finished` states (future issues).
- `leia` terminal input, exit codes, Monaco error markers.
