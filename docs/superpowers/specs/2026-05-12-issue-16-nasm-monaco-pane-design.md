# Issue #16 — Read-Only Monaco Panel for NASM Output

**Date:** 2026-05-12  
**Issue:** https://github.com/pm-avila/simples-editor/issues/16  
**PRD refs:** §5 RF06, §12.1

---

## Problem

The NASM pane is a placeholder `<aside>` with an empty body. Issue #16 replaces it with a real Monaco editor in read-only mode, ready to receive `.asm` content when the backend is connected in Sprint 3.

---

## Goals

1. The right panel uses Monaco in read-only mode with `language="asm"`.
2. The panel is ready to receive `.asm` content via a `value` prop.
3. Visual layout follows PRD §12.1: header "NASM x32" above the editor, dark theme.
4. The mock compiling message from issue #15 is preserved — shown as a comment inside Monaco when `status === "compiling"`.

---

## Architecture

### Updated `NasmPane`

Props:
```tsx
interface NasmPaneProps {
  status?: IdeStatus;   // "idle" | "compiling", default "idle"
  value?: string;       // ASM content to display, default ""
}
```

Rendering:
- Keep `<aside className="nasm-pane">` shell + `<header className="nasm-pane__header">NASM x32</header>`
- Replace `<div className="nasm-pane__body">` static content with a Monaco `<Editor>`:
  - `language="asm"` — Monaco built-in assembly highlighting
  - `theme={SIMPLES_THEME_ID}` — consistent dark theme
  - `options={{ readOnly: true, minimap: { enabled: false } }}`
  - `height="100%"`
  - `value={status === "compiling" ? "; compilando... (mock)" : (value ?? "")}`

The mock message (";  compilando... (mock)") is a valid assembly comment, so it renders correctly with syntax highlighting in the editor.

### CSS

`.nasm-pane__body` must have `flex: 1; overflow: hidden;` (already present from issue #14). No new CSS needed.

### Files changed

| File | Action |
|---|---|
| `frontend/src/components/ide/nasm-pane.tsx` | **MODIFY** — add Monaco editor |
| `tests/test_nasm_monaco_pane.py` | **CREATE** — source-based tests |

---

## Tests (source-based)

| # | Test | Assertion |
|---|---|---|
| 1 | `test_nasm_pane_imports_monaco_editor` | `nasm-pane.tsx` imports `Editor` from `@monaco-editor/react` |
| 2 | `test_nasm_pane_uses_asm_language` | `nasm-pane.tsx` contains `language="asm"` |
| 3 | `test_nasm_pane_is_readonly` | `nasm-pane.tsx` contains `readOnly: true` |
| 4 | `test_nasm_pane_accepts_value_prop` | `nasm-pane.tsx` contains `value?:` |
| 5 | `test_nasm_pane_mock_message_in_monaco` | `nasm-pane.tsx` contains `compilando` (value passed to Monaco when compiling) |

---

## Out of scope

- Syntax highlighting customisation for NASM (Monaco's built-in `asm` is sufficient for now).
- Horizontal splitter between top panels and terminal (future issue).
- Actual NASM content from backend (Sprint 3).
