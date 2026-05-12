# Issue #13 — Three-Panel IDE Shell Design

**Date:** 2026-05-12
**Issue:** [#13 feat(layout): build the three-panel IDE shell](https://github.com/pm-avila/simples-editor/issues/13)
**Status:** Approved

---

## Problem

The current `IdeShell` renders only `MonacoEditorPane` in a bare `<div>`. Issue #13 establishes the three-panel visual structure required by PRD §12.1: **editor** (left, top) | **NASM** (right, top) | **terminal** (full-width, bottom). Resizable splitters are deferred to issue #14.

---

## Approach

Use a **CSS Grid** layout in `IdeShell` with two rows: a top row containing the editor and NASM pane side-by-side (60 / 40 split), and a bottom row spanning the full width for the terminal. The splitter boundaries are visual only in this issue.

New placeholder components `NasmPane` and `TerminalPane` are extracted to their own files so each has a single clear responsibility and can be enhanced independently in later issues.

---

## Component Architecture

### `NasmPane` (`frontend/src/components/ide/nasm-pane.tsx`)
- Renders an `<aside>` with header "NASM x32" and an empty body.
- No props for now.

### `TerminalPane` (`frontend/src/components/ide/terminal-pane.tsx`)
- Renders a `<section>` with label "Terminal".
- No props for now.

### `IdeShell` (`frontend/src/components/ide/ide-shell.tsx`) — updated
- CSS Grid with `grid-template-areas`:
  ```
  "editor nasm"
  "terminal terminal"
  ```
- `grid-template-columns: 60fr 40fr`
- `grid-template-rows: 1fr 200px`
- Renders `<MonacoEditorPane />`, `<NasmPane />`, `<TerminalPane />`.

### Styles (`frontend/src/styles.css`) — updated
Add rules for `#ide-shell`, `.nasm-pane`, `.terminal-pane` to wire up the grid areas and basic dark background on placeholder panes.

---

## Layout

```
┌──────────────────────┬──────────────────────┐
│  .editor-area (60%)  │  .nasm-pane  (40%)    │
│  MonacoEditorPane    │  "NASM x32"           │
│                      │  (placeholder)        │
├──────────────────────┴──────────────────────┤
│  .terminal-pane  (100%)                      │
│  "Terminal"  (placeholder)                   │
└──────────────────────────────────────────────┘
```

---

## Testing (`tests/test_ide_shell_layout.py`)

Source-based contract tests:

1. `test_nasm_pane_module_exists` — `frontend/src/components/ide/nasm-pane.tsx` exists.
2. `test_terminal_pane_module_exists` — `frontend/src/components/ide/terminal-pane.tsx` exists.
3. `test_ide_shell_renders_all_three_panes` — `ide-shell.tsx` source contains `NasmPane` and `TerminalPane`.
4. `test_nasm_pane_has_header` — `nasm-pane.tsx` source contains the text `NASM x32`.
5. `test_terminal_pane_has_label` — `terminal-pane.tsx` source contains the text `Terminal`.

---

## Files Changed

| File | Action |
|---|---|
| `frontend/src/components/ide/nasm-pane.tsx` | CREATE |
| `frontend/src/components/ide/terminal-pane.tsx` | CREATE |
| `frontend/src/components/ide/ide-shell.tsx` | MODIFY |
| `frontend/src/styles.css` | MODIFY |
| `tests/test_ide_shell_layout.py` | CREATE |

---

## Acceptance Criteria (from issue)

- [x] Main screen uses three-panel layout: editor, NASM, terminal.
- [x] Shell respects the visual organisation for desktop (PRD §12.1).
- [x] Terminal is a placeholder in this stage.
