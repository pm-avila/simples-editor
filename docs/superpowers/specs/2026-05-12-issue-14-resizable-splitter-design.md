# Issue #14 — Resizable Editor / NASM Splitter

**Date:** 2026-05-12  
**Issue:** https://github.com/pm-avila/simples-editor/issues/14  
**PRD refs:** §5 RF07, §12.1

---

## Problem

The three-panel shell (issue #13) uses a fixed CSS Grid with `60fr 40fr` columns. The user cannot resize the editor or NASM panes, and there is no way to collapse the NASM pane.

---

## Goals

1. Vertical draggable splitter between the editor and the NASM pane.
2. Double-click on the resize handle collapses the NASM pane; second double-click restores it.
3. Terminal row (200 px) is NOT resizable in this issue — deferred to a future issue.

---

## Approach

Use **`react-resizable-panels`** (v2, by bvaughn). This library provides:

- `<PanelGroup direction="horizontal">` — replaces the CSS Grid top row.
- `<Panel>` — wraps each resizable pane with `defaultSize`, `minSize`, `collapsible` props.
- `<PanelResizeHandle>` — the drag handle between panels; has `onDoubleClick`.
- `ImperativePanel` API — `panel.collapse()` / `panel.expand()` for programmatic toggle.

### Why this library

- React-native (no extra DOM manipulation).
- Built-in collapsible with `collapse()` / `expand()` imperative API — exactly what double-click needs.
- Zero transitive runtime dependencies.
- Actively maintained and widely adopted.

---

## Architecture

### Layout change

Current `IdeShell` uses `display: grid` with `grid-template-areas` and `60fr 40fr` column split.

New layout:

```
#ide-shell  (flex-column, height: 100vh)
├── PanelGroup [direction=horizontal, flex: 1]
│   ├── Panel [editor, defaultSize=60, minSize=30]
│   │   └── MonacoEditorPane
│   ├── PanelResizeHandle [id="editor-nasm-handle"]
│   └── Panel [nasm, defaultSize=40, minSize=20, collapsible]
│       └── NasmPane
└── .terminal-area (height: 200px, flex-shrink: 0)
    └── TerminalPane
```

### Collapse / restore behaviour

- `PanelResizeHandle` receives `onDoubleClick` → calls `nasmPanelRef.current.collapse()` if expanded, or `nasmPanelRef.current.expand()` if collapsed.
- Collapse size: 0 (library default when `collapsible`).
- No minimum-size enforcement when collapsed (already covered by `collapsible`).

### CSS changes

- Remove `grid-template-areas`, `grid-template-columns`, `grid-template-rows` from `#ide-shell`.
- `#ide-shell` becomes `display: flex; flex-direction: column; height: 100vh`.
- `.editor-area` and `.nasm-area` CSS rules: remove `grid-area` declarations; add `height: 100%` on both (the `Panel` wrapper already fills the PanelGroup row).
- `.terminal-area`: `height: 200px; flex-shrink: 0` (already has `grid-area: terminal` — change to no grid-area, just height).
- Add `.resize-handle` style for the `<PanelResizeHandle>`: `width: 4px; background: #3c3c3c; cursor: col-resize; transition: background 0.15s`.
- On hover/active: `background: #007acc`.

### Files changed

| File | Change |
|---|---|
| `frontend/package.json` | add `react-resizable-panels` dep |
| `frontend/src/components/ide/ide-shell.tsx` | replace CSS Grid top row with `PanelGroup` + `PanelResizeHandle` + collapse logic |
| `frontend/src/styles.css` | remove grid columns/rows; add flex-column + `.resize-handle` styles |
| `tests/test_ide_splitter.py` | NEW: source-based tests for splitter contract |

### No change needed

- `monaco-editor-pane.tsx` — already uses `height="100%"` after issue #13 fix.
- `nasm-pane.tsx`, `terminal-pane.tsx` — unchanged.

---

## Tests (source-based)

All tests read `.tsx`/`.ts` source files and assert string presence.

| # | Test name | Assertion |
|---|---|---|
| 1 | `test_ide_shell_imports_panel_group` | `ide-shell.tsx` imports `PanelGroup` from `react-resizable-panels` |
| 2 | `test_ide_shell_imports_panel_resize_handle` | `ide-shell.tsx` imports `PanelResizeHandle` |
| 3 | `test_nasm_panel_is_collapsible` | `ide-shell.tsx` contains `collapsible` attribute |
| 4 | `test_resize_handle_has_double_click` | `ide-shell.tsx` contains `onDoubleClick` on resize handle |
| 5 | `test_resize_handle_style_in_css` | `styles.css` contains `.resize-handle` rule |
| 6 | `test_panel_group_replaces_grid_columns` | `styles.css` does NOT contain `grid-template-columns` (top row removed) |

---

## Out of scope

- Horizontal top|terminal splitter (future issue).
- Persisting panel sizes across sessions (no localStorage in this issue).
- Mobile layout (deferred to v1.1 per PRD §12.1).
