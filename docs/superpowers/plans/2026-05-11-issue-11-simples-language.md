# Issue #11 SIMPLES Language Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Registrar a linguagem `simples` no Monaco e fazer o editor principal usar esse contrato de tokenização.

**Architecture:** A implementação extrai a definição da linguagem SIMPLES para um módulo dedicado do Monaco, com lista de palavras reservadas e tokenizer Monarch em um único ponto. `MonacoEditorPane` apenas chama o registrador antes da montagem do editor e troca `defaultLanguage` para `simples`, mantendo a UI desacoplada da configuração léxica.

**Tech Stack:** React 18, TypeScript 5, Monaco Editor (`@monaco-editor/react`, `monaco-editor`), Python `unittest`

---

### File structure

- Create: `frontend/src/components/ide/simples-language.ts` — contrato da linguagem `simples`, incluindo palavras reservadas, tokenizer Monarch e helper de registro.
- Modify: `frontend/src/components/ide/monaco-editor-pane.tsx` — registrar a linguagem antes do mount e trocar o editor para `simples`.
- Create: `tests/test_simples_language.py` — contrato source-based para palavras reservadas, tokenizer e integração com o editor.

### Task 1: Travar o contrato da linguagem SIMPLES

**Files:**
- Create: `tests/test_simples_language.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_simples_language.py`:

```python
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SimplesLanguageContractTest(unittest.TestCase):
    def test_simples_language_module_exists(self):
        path = ROOT / "frontend" / "src" / "components" / "ide" / "simples-language.ts"
        self.assertTrue(path.exists(), f"missing: {path}")

    def test_keywords_match_prd_contract(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "simples-language.ts"
        ).read_text(encoding="utf-8")
        expected_keywords = [
            "programa", "inicio", "fim",
            "inteiro", "flutuante", "vazio",
            "se", "entao", "senao", "fimse",
            "enquanto", "fimenquanto",
            "para", "de", "ate", "passo", "faca", "fimpara",
            "leia", "escreva", "escreval",
            "e", "ou", "nao",
            "div",
            "procedimento", "retorna",
        ]
        for keyword in expected_keywords:
            self.assertIn(f'"{keyword}"', content)

    def test_tokenizer_covers_prd_operator_delimiter_and_numbers(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "simples-language.ts"
        ).read_text(encoding="utf-8")
        self.assertIn('operators: ["<-", "+", "-", "*", "div", ">", "<", "=", "<>", ">=", "<="]', content)
        self.assertIn(r'/\\d+\\.\\d+/', content)
        self.assertIn(r'/\\d+/', content)
        self.assertIn(r'/[(),;]/', content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples && .venv/bin/python -m unittest tests/test_simples_language.py -v`
Expected: FAIL with missing `frontend/src/components/ide/simples-language.ts`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/components/ide/simples-language.ts`:

```ts
import type * as Monaco from "monaco-editor";


export const SIMPLES_LANGUAGE_ID = "simples";

export const SIMPLES_KEYWORDS = [
  "programa", "inicio", "fim",
  "inteiro", "flutuante", "vazio",
  "se", "entao", "senao", "fimse",
  "enquanto", "fimenquanto",
  "para", "de", "ate", "passo", "faca", "fimpara",
  "leia", "escreva", "escreval",
  "e", "ou", "nao",
  "div",
  "procedimento", "retorna",
] as const;


let isRegistered = false;


export function registerSimplesLanguage(monaco: typeof Monaco) {
  if (isRegistered) {
    return;
  }

  monaco.languages.register({ id: SIMPLES_LANGUAGE_ID });
  monaco.languages.setMonarchTokensProvider(SIMPLES_LANGUAGE_ID, {
    ignoreCase: true,
    keywords: SIMPLES_KEYWORDS,
    operators: ["<-", "+", "-", "*", "div", ">", "<", "=", "<>", ">=", "<="],
    symbols: /[=<>+\-*]+/,
    tokenizer: {
      root: [
        [/[a-zA-Z_]\w*/, { cases: { "@keywords": "keyword", "@default": "identifier" } }],
        [/\d+\.\d+/, "number.float"],
        [/\d+/, "number"],
        [/<-/, "operator"],
        [/@symbols/, { cases: { "@operators": "operator", "@default": "" } }],
        [/[(),;]/, "delimiter"],
        [/\s+/, "white"],
      ],
    },
  });

  isRegistered = true;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples && .venv/bin/python -m unittest tests/test_simples_language.py -v`
Expected: PASS with 3 tests, 0 failures

- [ ] **Step 5: Commit**

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples
git add tests/test_simples_language.py frontend/src/components/ide/simples-language.ts
git commit -m "test: add SIMPLES language contract" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Integrar a linguagem `simples` ao Monaco principal

**Files:**
- Modify: `frontend/src/components/ide/monaco-editor-pane.tsx`
- Modify: `tests/test_simples_language.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_simples_language.py`:

```python
class SimplesLanguageIntegrationTest(unittest.TestCase):
    def test_editor_registers_language_before_mount_and_uses_simples(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("registerSimplesLanguage", content)
        self.assertIn("beforeMount", content)
        self.assertIn('defaultLanguage="simples"', content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples && .venv/bin/python -m unittest tests/test_simples_language.py -v`
Expected: FAIL because `monaco-editor-pane.tsx` still uses `python` and does not register the SIMPLES language

- [ ] **Step 3: Write minimal implementation**

Update `frontend/src/components/ide/monaco-editor-pane.tsx`:

```tsx
import Editor from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { registerSimplesLanguage } from "./simples-language";


interface MonacoEditorPaneProps {
  initialValue?: string;
}


export function MonacoEditorPane({ initialValue = "" }: MonacoEditorPaneProps) {
  function onChange(_value: string | undefined) {
    // handle editor content changes
  }

  function beforeMount(monaco: typeof Monaco) {
    registerSimplesLanguage(monaco);
  }

  return (
    <Editor
      height="90vh"
      beforeMount={beforeMount}
      defaultLanguage="simples"
      defaultValue={initialValue}
      onChange={onChange}
    />
  );
}
```

- [ ] **Step 4: Run tests and build to verify they pass**

Run: `cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples && .venv/bin/python -m unittest tests/test_simples_language.py tests/test_monaco_main_route.py -v && cd frontend && npm run build`
Expected: Python tests PASS and frontend build succeeds

- [ ] **Step 5: Commit**

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples
git add tests/test_simples_language.py frontend/src/components/ide/monaco-editor-pane.tsx
git commit -m "feat: register SIMPLES Monaco language" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
