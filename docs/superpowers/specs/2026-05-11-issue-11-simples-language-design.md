# Issue #11 Design: Register the SIMPLES Monaco language

## Problem

Issue #11 must make the editor recognize the SIMPLES language so the Monaco foundation added in issue #10 can evolve into real syntax highlighting. Today the editor still uses `defaultLanguage="python"`, so none of the SIMPLES-specific reserved words, operators, delimiters, or numbers are tokenized according to the PRD.

## Scope

This design covers **only issue #11**.

Included:
- Register the Monaco language id `simples`.
- Define the 27 reserved words from the PRD in one shared source of truth.
- Add a Monarch tokenizer for keywords, identifiers, operators, delimiters, integers, and floating-point numbers.
- Wire the editor pane to use `simples` instead of `python`.

Excluded:
- Dark theme colors (#12).
- Three-panel shell (#13).
- Splitters (#14).
- Run flow (#15).
- NASM read-only Monaco panel (#16).

## Recommended approach

Use a **dedicated Monaco language module** plus a small integration point in `MonacoEditorPane`.

Recommended flow:

1. Create a focused `simples-language` module that exports the keyword list and a `registerSimplesLanguage(monaco)` helper.
2. Call that helper from Monaco's setup hook in the editor component.
3. Switch the editor language from `python` to `simples`.

This is better than embedding tokenizer logic directly in the component because issue #12 will need to build on the same Monaco setup surface for theming. A dedicated module keeps the language contract isolated and reusable.

## Architecture

Issue #11 should introduce two bounded pieces:

### 1. SIMPLES language contract

One file owns:
- the 27 reserved words
- operator and delimiter definitions
- the Monarch tokenizer configuration
- the registration helper for Monaco

This keeps the PRD mapping explicit and prevents tokenizer details from leaking into UI components.

### 2. Monaco editor integration

`MonacoEditorPane` remains responsible for rendering the editor, but it should delegate language setup to the registration helper. The component should:
- register the language before the editor mounts
- set the editor language to `simples`
- keep the rest of the editor behavior unchanged

## Data flow

1. `MonacoEditorPane` receives Monaco's setup callback.
2. The setup callback calls `registerSimplesLanguage(monaco)`.
3. The helper registers `simples` and its Monarch tokenizer.
4. The editor instance is created with `defaultLanguage="simples"`.
5. Monaco tokenizes SIMPLES source according to the registered language contract.

## Error handling

The registration helper should be safe to call repeatedly from the component lifecycle. Repeated registration must not crash the app or create conflicting language state. If a guard is needed, it should be local to the language module instead of scattered through UI code.

## Validation strategy

Validation should prove both the contract and the integration:

- Source-based tests assert the SIMPLES language module exists and contains the 27 PRD keywords.
- Tests assert the tokenizer covers operators, delimiters, integers, and floats from the PRD summary.
- Tests assert `MonacoEditorPane` registers the language and uses `defaultLanguage="simples"`.
- The frontend build must still succeed after the Monaco integration changes.

## Sequence note

Issue #11 should stop at language registration. Theme colors stay isolated to issue #12 so the tokenizer and theming layers remain independently reviewable through separate PRs.
