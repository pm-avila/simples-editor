# Issue #12 SIMPLES Dark Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aplicar um tema dark customizado ao editor Monaco usando a paleta PRD §13.1 (keywords ciano, números laranja, identificadores neutros).

**Architecture:** Um módulo dedicado `simples-theme.ts` exporta `SIMPLES_THEME_ID` e `defineSimplesDarkTheme(monaco)` com guard de idempotência, seguindo o mesmo padrão de `simples-language.ts`. `MonacoEditorPane` chama ambos os registradores em `beforeMount` e passa `theme={SIMPLES_THEME_ID}` ao `<Editor>`.

**Tech Stack:** React 18, TypeScript 5, Monaco Editor (`@monaco-editor/react`, `monaco-editor`), Python `unittest`

---

### File structure

- Create: `frontend/src/components/ide/simples-theme.ts` — exporta `SIMPLES_THEME_ID` e `defineSimplesDarkTheme(monaco)` com a paleta PRD.
- Modify: `frontend/src/components/ide/monaco-editor-pane.tsx` — importa e chama `defineSimplesDarkTheme` em `beforeMount`, adiciona `theme={SIMPLES_THEME_ID}`.
- Create: `tests/test_simples_theme.py` — testes de contrato source-based para o módulo de tema.

---

### Task 1: Travar o contrato do tema dark

**Files:**
- Create: `tests/test_simples_theme.py`
- Create: `frontend/src/components/ide/simples-theme.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/test_simples_theme.py`:

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SimplesThemeContractTest(unittest.TestCase):
    def test_simples_theme_module_exists(self):
        path = ROOT / "frontend" / "src" / "components" / "ide" / "simples-theme.ts"
        self.assertTrue(path.exists(), f"missing: {path}")

    def test_theme_id_constant_present(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "simples-theme.ts"
        ).read_text(encoding="utf-8")
        self.assertIn('SIMPLES_THEME_ID = "simples-dark"', content)

    def test_token_colour_rules_present(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "simples-theme.ts"
        ).read_text(encoding="utf-8")
        self.assertIn("4FC1FF", content)   # keyword cyan
        self.assertIn("FFB347", content)   # number orange
        self.assertIn("D4D4D4", content)   # identifier neutral


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-12 && ../../.venv/bin/python -m unittest tests/test_simples_theme.py -v
```
Expected: FAIL — module file does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/components/ide/simples-theme.ts`:

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

- [ ] **Step 4: Run test to verify it passes**

Run:
```
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-12 && ../../.venv/bin/python -m unittest tests/test_simples_theme.py -v
```
Expected: 3 tests pass, 0 failures.

- [ ] **Step 5: Commit**

```bash
git -C /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-12 add tests/test_simples_theme.py frontend/src/components/ide/simples-theme.ts
git -C /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-12 commit -m "test: add SIMPLES dark theme contract" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Integrar o tema ao MonacoEditorPane

**Files:**
- Modify: `frontend/src/components/ide/monaco-editor-pane.tsx`
- Modify: `tests/test_simples_theme.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_simples_theme.py` (after the existing class, before `if __name__ == "__main__"`):

```python
class SimplesThemeIntegrationTest(unittest.TestCase):
    def test_editor_uses_theme_constant(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("defineSimplesDarkTheme", content)
        self.assertIn("SIMPLES_THEME_ID", content)
        self.assertIn("theme={SIMPLES_THEME_ID}", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-12 && ../../.venv/bin/python -m unittest tests/test_simples_theme.py -v
```
Expected: 3 pass, 1 fail — `monaco-editor-pane.tsx` not yet updated.

- [ ] **Step 3: Write minimal implementation**

Replace the ENTIRE content of `frontend/src/components/ide/monaco-editor-pane.tsx` with:

```tsx
import Editor from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { registerSimplesLanguage, SIMPLES_LANGUAGE_ID } from "./simples-language";
import { defineSimplesDarkTheme, SIMPLES_THEME_ID } from "./simples-theme";


interface MonacoEditorPaneProps {
  initialValue?: string;
}


export function MonacoEditorPane({ initialValue = "" }: MonacoEditorPaneProps) {
  function onChange(_value: string | undefined) {
    // handle editor content changes
  }

  function beforeMount(monaco: typeof Monaco) {
    registerSimplesLanguage(monaco);
    defineSimplesDarkTheme(monaco);
  }

  return (
    <Editor
      height="90vh"
      beforeMount={beforeMount}
      defaultLanguage={SIMPLES_LANGUAGE_ID}
      defaultValue={initialValue}
      theme={SIMPLES_THEME_ID}
      onChange={onChange}
    />
  );
}
```

- [ ] **Step 4: Run tests and build to verify they pass**

Run:
```
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-12 && ../../.venv/bin/python -m unittest tests/test_simples_theme.py tests/test_simples_language.py tests/test_monaco_main_route.py -v && cd frontend && npm run build
```
Expected: All Python tests pass, Vite build succeeds.

- [ ] **Step 5: Commit**

```bash
git -C /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-12 add tests/test_simples_theme.py frontend/src/components/ide/monaco-editor-pane.tsx
git -C /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/.worktrees/feat-12 commit -m "feat: apply SIMPLES dark theme to Monaco editor" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
