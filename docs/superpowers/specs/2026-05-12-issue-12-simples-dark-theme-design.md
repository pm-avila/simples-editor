# Issue #12 — SIMPLES Dark Theme Design

**Date:** 2026-05-12
**Issue:** [#12 feat(editor): apply dark theme for SIMPLES syntax](https://github.com/pm-avila/simples-editor/issues/12)
**Status:** Approved

---

## Problem

The Monaco editor currently renders SIMPLES source code with the default VS Code dark theme token colours, which do not honour the SIMPLES-specific palette defined in PRD §13.1. Keywords, numbers, identifiers and (future) comments need their own colours to improve legibility and reinforce SIMPLES's visual identity.

---

## Approach

A dedicated `simples-theme.ts` module (mirroring the `simples-language.ts` pattern) exports two public symbols:

- `SIMPLES_THEME_ID` — the string `"simples-dark"`, used consistently wherever the theme is referenced.
- `defineSimplesDarkTheme(monaco)` — calls `monaco.editor.defineTheme(SIMPLES_THEME_ID, …)` with the PRD colour palette and an idempotency guard.

`MonacoEditorPane` imports both, calls `defineSimplesDarkTheme` in its `beforeMount` prop (just after `registerSimplesLanguage`), and passes `theme={SIMPLES_THEME_ID}` to the `<Editor>` component.

---

## Token Colour Palette (PRD §13.1)

| Token | Colour | Hex |
|---|---|---|
| `keyword` | cyan | `#4FC1FF` |
| `number` | orange | `#FFB347` |
| `number.float` | orange | `#FFB347` |
| `identifier` | neutral (default foreground) | `#D4D4D4` |
| `comment` | green (reserved, future use) | `#6A9955` |
| `operator` | neutral | `#D4D4D4` |
| `delimiter` | neutral | `#D4D4D4` |

Base: `vs-dark`, `inherit: true` — all other Monaco defaults are inherited.

---

## Module: `simples-theme.ts`

```ts
import type * as Monaco from "monaco-editor";

export const SIMPLES_THEME_ID = "simples-dark";

let isDefined = false;

export function defineSimplesDarkTheme(monaco: typeof Monaco) {
  if (isDefined) return;

  monaco.editor.defineTheme(SIMPLES_THEME_ID, {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword",      foreground: "4FC1FF" },
      { token: "number.float", foreground: "FFB347" },
      { token: "number",       foreground: "FFB347" },
      { token: "identifier",   foreground: "D4D4D4" },
      { token: "comment",      foreground: "6A9955", fontStyle: "italic" },
      { token: "operator",     foreground: "D4D4D4" },
      { token: "delimiter",    foreground: "D4D4D4" },
    ],
    colors: {},
  });

  isDefined = true;
}
```

---

## Component Update: `monaco-editor-pane.tsx`

```tsx
import { registerSimplesLanguage, SIMPLES_LANGUAGE_ID } from "./simples-language";
import { defineSimplesDarkTheme, SIMPLES_THEME_ID } from "./simples-theme";

// inside beforeMount:
function beforeMount(monaco: typeof Monaco) {
  registerSimplesLanguage(monaco);
  defineSimplesDarkTheme(monaco);
}

// on <Editor>:
<Editor
  height="90vh"
  beforeMount={beforeMount}
  defaultLanguage={SIMPLES_LANGUAGE_ID}
  defaultValue={initialValue}
  theme={SIMPLES_THEME_ID}
  onChange={onChange}
/>
```

---

## Testing (`tests/test_simples_theme.py`)

Source-based contract tests (same pattern as `test_simples_language.py`):

1. `test_simples_theme_module_exists` — file `frontend/src/components/ide/simples-theme.ts` exists.
2. `test_theme_id_constant_present` — source contains `SIMPLES_THEME_ID = "simples-dark"`.
3. `test_token_colour_rules_present` — source contains hex values for keyword (`4FC1FF`), number (`FFB347`), and identifier (`D4D4D4`).
4. `test_editor_uses_theme_constant` (integration, in `SimplesThemeIntegrationTest`) — `monaco-editor-pane.tsx` source contains `defineSimplesDarkTheme`, `SIMPLES_THEME_ID`, and `theme={SIMPLES_THEME_ID}`.

All tests must pass with `../../.venv/bin/python -m unittest tests/test_simples_theme.py -v`.

---

## Files Changed

| File | Action |
|---|---|
| `frontend/src/components/ide/simples-theme.ts` | CREATE |
| `frontend/src/components/ide/monaco-editor-pane.tsx` | MODIFY |
| `tests/test_simples_theme.py` | CREATE |

---

## Acceptance Criteria (from issue)

- [x] Editor applies custom dark theme for the SIMPLES language.
- [x] Keywords (cyan), numbers (orange), identifiers (neutral) respect the PRD §13.1 palette.
- [x] Theme configuration works together with the custom tokenizer (both registered in `beforeMount`).
