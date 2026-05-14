# Issue #10 Design: Monaco foundation on the main route

## Problem

Issue #10 must place Monaco Editor on the main IDE route and align the frontend with the stack defined in the PRD. The current frontend is still a minimal static HTML/JS login shell, so this issue also needs to establish the application foundation that later editor and layout issues can build on without rework.

## Scope

This design covers **only issue #10**.

Included:
- Migrate the frontend foundation to the stack defined in the PRD.
- Render the main IDE route with an editable Monaco instance as the primary content.
- Keep the initial screen focused on a single editor area.
- Leave clear extension points for later issues in the same sequence.

Excluded:
- Custom SIMPLES language registration (#11).
- Custom dark theme (#12).
- Three-panel IDE shell (#13).
- Splitters (#14).
- Mock run flow (#15).
- Read-only NASM Monaco panel (#16).

## Recommended approach

Use issue #10 as the **foundation PR** for the whole editor sequence:

1. Replace the current static frontend base with the PRD-aligned frontend stack.
2. Deliver a single main route that renders Monaco as an editable code area.
3. Keep the page structure intentionally simple so later issues can layer language support, theme, layout, splitters, toolbar behavior, and NASM rendering without rewriting the editor component.

This is preferred over combining multiple editor issues into one PR because it preserves the per-issue workflow, keeps review scope small, and reduces the risk of mixing acceptance criteria.

## Architecture

Issue #10 establishes three main layers:

### 1. Application shell

The new frontend entrypoint owns app bootstrap, routing, and the top-level IDE page render. For this issue, the main route only needs to render a simple IDE page with a title/container and the editor region.

### 2. IDE page

The page component provides the main route structure. It should remain intentionally minimal for this issue: one editor-focused view with stable container boundaries that later issues can extend with toolbar, NASM panel, and terminal regions.

### 3. Monaco editor component

This component wraps `@monaco-editor/react` and exposes the minimum API needed now:
- initial content
- current content updates
- editable mode

It should also be structured so later issues can add props such as:
- `language`
- `theme`
- `readOnly`
- externally supplied content

## Data flow

For issue #10, data flow is local and straightforward:

1. The app loads the main route.
2. The main route renders the IDE page.
3. The IDE page renders the Monaco wrapper.
4. The Monaco wrapper initializes with starter code/content.
5. User edits update local UI state so typing, selection, and standard editor shortcuts work naturally.

There is no backend interaction, compile action, NASM output, or terminal state in this issue.

## Error handling

Error handling for this issue should be explicit and visible:

- If Monaco or the frontend app fails to initialize, the UI should show a visible failure state instead of silently rendering an empty shell.
- Since compile and runtime behaviors are out of scope here, no execution-state error handling is introduced yet.

This keeps failure modes clear while avoiding placeholder logic that belongs to later issues.

## Validation strategy

Validation for issue #10 should prove both the new base and the editor integration:

- Frontend build succeeds on the new stack.
- The main route includes the IDE surface and Monaco integration.
- The editor remains editable so the acceptance criteria for writing, editing, and selecting code are met.

The testing and structure from this issue should make the next PRs incremental:
- #11 adds language registration
- #12 adds theme
- #13 adds the three-panel shell
- #14 adds splitters
- #15 adds mock run state
- #16 adds the read-only NASM Monaco panel

## Sequence note

The broader execution order remains:

1. #10 Monaco foundation on the main route
2. #11 SIMPLES language registration
3. #12 custom dark theme
4. #13 three-panel IDE shell
5. #14 resizable splitters
6. #15 mock run toolbar behavior
7. #16 NASM read-only Monaco panel

Each item should be delivered through the documented workflow: start from `dev`, create `feat/<issue-number>`, implement the scoped change, open a PR to `dev`, review, merge, and update PR evidence after merge.
