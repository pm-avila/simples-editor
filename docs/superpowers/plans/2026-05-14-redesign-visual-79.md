# Visual Redesign (Issue #79) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completely redesign the Simples Editor frontend with a NERD/Dracula aesthetic for the landing page and retro 80s/90s phosphor terminal theme for the IDE, using CSS-only animations.

**Architecture:** Implement in 6 atomic phases from CSS foundation → landing page → IDE effects → Monaco theme → toolbar/terminal styling → testing. Each phase produces working, testable UI increments committed independently. Landing page ships Dracula (purple/pink) with ASCII art and typing animation. IDE ships amber phosphor with scanlines, glow, flicker, and CRT border effects applied to editor, toolbar, and terminal.

**Tech Stack:** HTML5, CSS3 (custom properties, keyframes, gradients), Google Fonts (JetBrains Mono, Fira Code, VT323, Share Tech Mono), Monaco Editor, xterm.js, React (existing).

---

## File Structure

**Modified Files:**
- `frontend/index.html` - Add 4 Google Fonts links (JetBrains Mono, Fira Code, VT323, Share Tech Mono)
- `frontend/src/styles.css` - Add CSS variables (--dracula-*, --retro-*), @keyframes (typing, flicker), utility classes (.scanlines, .phosphor-glow)
- `frontend/src/components/auth/login-screen.tsx` - Landing page: add ASCII art `<pre>`, typing animation CSS, Dracula form styling
- `frontend/src/components/ide/ide-shell.tsx` - IDE container: add CRT effects, scanlines overlay, flicker animation
- `frontend/src/components/ide/toolbar.tsx` - DOS-style bevel borders, VT323 font, status bar layout
- `frontend/src/components/ide/terminal-pane.tsx` - Pass amber phosphor theme config to xterm.js

**New Files:**
- `frontend/src/components/ide/retro-theme.ts` - Monaco editor theme with amber retro colors

---

## Phase 1: CSS Foundation

### Task 1: Add Google Fonts to index.html

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: Open index.html and locate the `<head>` section**

Run: `grep -n "<head>" /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/frontend/index.html`

Expected: Find the `<head>` opening tag (typically line 5-10)

- [ ] **Step 2: Add Google Fonts links before `</head>`**

Insert after existing `<meta>` tags but before `</head>`:

```html
<!-- Google Fonts for visual redesign -->
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
```

- [ ] **Step 3: Verify fonts load**

Run: `npm run dev` (start dev server in background), then open browser dev tools → Network tab. Confirm 4 font requests succeed (200 status).

- [ ] **Step 4: Commit**

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples
git add frontend/index.html
git commit -m "feat(79): add Google Fonts for visual redesign (JetBrains Mono, Fira Code, VT323, Share Tech Mono)"
```

---

### Task 2: Add CSS variables and utility classes

**Files:**
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Open styles.css and locate the top of the file**

Run: `head -50 /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/frontend/src/styles.css`

- [ ] **Step 2: Add CSS custom properties after any existing variables (before main styles)**

Insert at the top of styles.css after any reset rules:

```css
/* Visual Redesign Theme Variables (Issue #79) */
:root {
  /* Dracula Theme (Landing Page) */
  --dracula-bg: #282a36;
  --dracula-fg: #f8f8f2;
  --dracula-purple: #bd93f9;
  --dracula-pink: #ff79c6;
  --dracula-blue: #8be9fd;
  --dracula-green: #50fa7b;

  /* Retro Amber Phosphor Theme (IDE) */
  --retro-bg: #0a0800;
  --retro-fg: #ffb000;
  --retro-glow: #ff9000;
  --retro-dim: #cc6600;
  --retro-scanline: rgba(0, 0, 0, 0.15);

  /* Typography */
  --font-jetbrains-mono: 'JetBrains Mono', monospace;
  --font-fira-code: 'Fira Code', monospace;
  --font-vt323: 'VT323', monospace;
  --font-share-tech: 'Share Tech Mono', monospace;
}
```

- [ ] **Step 3: Add @keyframes for typing animation**

Add after CSS variables:

```css
@keyframes typing-cursor {
  0%, 49% { border-right-color: var(--dracula-purple); }
  50%, 100% { border-right-color: transparent; }
}

@keyframes typing {
  from { width: 0; }
  to { width: 100%; }
}

@keyframes flicker {
  0%, 18%, 22%, 25%, 54%, 56%, 100% { opacity: 1; }
  20%, 24%, 55% { opacity: 0.5; }
}
```

- [ ] **Step 4: Add utility classes for scanlines and phosphor glow**

Add after keyframes:

```css
.scanlines {
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    var(--retro-scanline),
    var(--retro-scanline) 1px,
    transparent 1px,
    transparent 2px
  );
  z-index: 9999;
  pointer-events: none;
}

.phosphor-glow {
  color: var(--retro-fg);
  text-shadow:
    0 0 10px var(--retro-glow),
    0 0 20px var(--retro-glow),
    0 0 30px var(--retro-dim);
}

.phosphor-flicker {
  animation: flicker 0.15s infinite;
}
```

- [ ] **Step 5: Test CSS loads correctly**

Run: `npm run dev`, then in browser dev tools → Elements tab → check <root> element shows CSS custom properties in computed styles.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/styles.css
git commit -m "feat(79): add CSS variables (Dracula, Amber Phosphor), keyframes (typing, flicker), utility classes"
```

---

## Phase 2: Landing Page (Dracula Theme)

### Task 3: Create landing page ASCII art and typing animation

**Files:**
- Modify: `frontend/src/components/auth/login-screen.tsx`

- [ ] **Step 1: View current login-screen.tsx to understand structure**

Run: `head -100 /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/frontend/src/components/auth/login-screen.tsx`

- [ ] **Step 2: Add ASCII art and typing animation styles to the component**

Add new CSS styles to the component file (or reference from styles.css):

```css
.landing-container {
  background: var(--dracula-bg);
  color: var(--dracula-fg);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: var(--font-jetbrains-mono);
  padding: 2rem;
}

.landing-logo {
  font-family: var(--font-jetbrains-mono);
  font-weight: bold;
  font-size: 1.5rem;
  color: var(--dracula-purple);
  margin-bottom: 2rem;
  white-space: pre;
  text-align: center;
}

.landing-title {
  font-size: 2.5rem;
  color: var(--dracula-purple);
  margin-bottom: 1rem;
  animation: typing 3s steps(20, end);
  overflow: hidden;
  border-right: 3px solid var(--dracula-purple);
  animation: typing 3s steps(20, end), typing-cursor 0.5s infinite;
}

.landing-form {
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid var(--dracula-purple);
  border-radius: 4px;
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 0 20px rgba(189, 147, 249, 0.2);
}

.landing-form input {
  background: var(--dracula-bg);
  color: var(--dracula-fg);
  border: 1px solid var(--dracula-purple);
  padding: 0.75rem;
  margin-bottom: 1rem;
  width: 100%;
  font-family: var(--font-fira-code);
  box-sizing: border-box;
}

.landing-form button {
  background: var(--dracula-purple);
  color: var(--dracula-bg);
  border: none;
  padding: 0.75rem 1.5rem;
  width: 100%;
  cursor: pointer;
  font-weight: bold;
  font-family: var(--font-jetbrains-mono);
  transition: all 0.3s ease;
}

.landing-form button:hover {
  background: var(--dracula-pink);
  box-shadow: 0 0 20px rgba(255, 121, 198, 0.5);
}
```

- [ ] **Step 3: Replace login-screen.tsx JSX with Dracula-themed version**

Replace the render section:

```tsx
return (
  <div className="landing-container">
    <pre className="landing-logo">{`
  ███████╗██╗███╗   ███╗██████╗ ██╗     ███████╗███████╗
  ██╔════╝██║████╗ ████║██╔══██╗██║     ██╔════╝██╔════╝
  ███████╗██║██╔████╔██║██████╔╝██║     █████╗  █████╗
  ╚════██║██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ██╔══╝
  ███████║██║██║ ╚═╝ ██║██║     ███████╗███████╗███████╗
  ╚══════╝╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚══════╝
    `}</pre>
    <h1 className="landing-title">VISUAL SIMPLES</h1>
    <form className="landing-form" onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="user@example.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">LOGIN</button>
    </form>
    <div style={{ marginTop: '2rem', fontSize: '0.875rem', color: 'var(--dracula-blue)' }}>
      Powered by Simples • Compiled Code Editor
    </div>
  </div>
);
```

- [ ] **Step 4: Test in browser**

Run: `npm run dev`, navigate to login page. Verify:
- Dark purple background (Dracula)
- ASCII art SIMPLES logo displays correctly
- Title animates with typing effect
- Form has purple borders and glow effect
- Button changes color on hover

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/auth/login-screen.tsx
git commit -m "feat(79): redesign landing page with Dracula theme, ASCII art, typing animation"
```

---

## Phase 3: IDE Effects (Scanlines, Glow, Flicker)

### Task 4: Add CRT effects to IDE container

**Files:**
- Modify: `frontend/src/components/ide/ide-shell.tsx`

- [ ] **Step 1: View ide-shell.tsx structure**

Run: `head -100 /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/frontend/src/components/ide/ide-shell.tsx`

- [ ] **Step 2: Add retro IDE styles**

Add to component CSS:

```css
.ide-container {
  background: var(--retro-bg);
  color: var(--retro-fg);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: var(--font-share-tech);
  border: 3px solid;
  border-color: #ccc #666 #666 #ccc;
  box-shadow: inset 1px 1px 0 #fff, inset -1px -1px 0 #000, 3px 3px 0 rgba(0, 0, 0, 0.5);
}

.ide-editor {
  flex: 1;
  overflow: auto;
  background: var(--retro-bg);
  animation: flicker 0.15s infinite 50ms;
}

.ide-content {
  position: relative;
  width: 100%;
  height: 100%;
}
```

- [ ] **Step 3: Add scanlines overlay to JSX**

Wrap the IDE content with:

```tsx
<div className="ide-container">
  <div className="ide-content">
    {/* existing IDE content */}
  </div>
  <div className="scanlines"></div>
</div>
```

- [ ] **Step 4: Test visual effects**

Run: `npm run dev`, open IDE view. Verify:
- Dark background with amber text
- Scanlines overlay (thin horizontal lines)
- Slight flicker animation (subtle opacity changes)
- DOS-style 3D border effect on container

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ide/ide-shell.tsx
git commit -m "feat(79): add CRT effects (scanlines, flicker, DOS border) to IDE container"
```

---

## Phase 4: Monaco Editor Theme

### Task 5: Create retro-theme.ts for Monaco editor

**Files:**
- Create: `frontend/src/components/ide/retro-theme.ts`

- [ ] **Step 1: Create new file with Monaco theme config**

Create file `/Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/frontend/src/components/ide/retro-theme.ts`:

```typescript
export const retroTheme = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '#cc6600', fontStyle: 'italic' },
    { token: 'string', foreground: '#ffb000' },
    { token: 'number', foreground: '#ff9000' },
    { token: 'builtin', foreground: '#ffb000' },
    { token: 'keyword', foreground: '#ff9000', fontStyle: 'bold' },
    { token: 'operator', foreground: '#ffb000' },
    { token: 'type', foreground: '#ffb000', fontStyle: 'bold' },
    { token: 'variable', foreground: '#ffb000' },
    { token: 'function', foreground: '#ffb000', fontStyle: 'bold' },
    { token: 'invalid', foreground: '#ff0000', background: '#0a0800' },
  ],
  colors: {
    'editor.background': '#0a0800',
    'editor.foreground': '#ffb000',
    'editor.lineNumbersActiveForeground': '#ffb000',
    'editor.lineNumbersForeground': '#cc6600',
    'editor.selectionBackground': 'rgba(255, 176, 0, 0.2)',
    'editor.selectionHighlightBackground': 'rgba(255, 144, 0, 0.15)',
    'editor.wordHighlightBackground': 'rgba(255, 144, 0, 0.1)',
    'editorCursor.foreground': '#ffb000',
    'editorWhitespace.foreground': 'rgba(255, 176, 0, 0.2)',
    'editorLineNumber.background': '#0a0800',
    'editorLineNumber.foreground': '#cc6600',
    'editorGutter.background': '#0a0800',
    'editor.rangeHighlightBackground': 'rgba(255, 176, 0, 0.05)',
  },
};
```

- [ ] **Step 2: Import and apply theme in editor initialization**

In `frontend/src/components/ide/editor-pane.tsx` (or wherever Monaco is initialized), add:

```typescript
import { retroTheme } from './retro-theme';

// In editor init:
monaco.editor.defineTheme('retro-amber', retroTheme);
monaco.editor.setTheme('retro-amber');
```

- [ ] **Step 3: Test Monaco theme applies**

Run: `npm run dev`, open IDE and create/open a file. Verify:
- Editor background is dark (#0a0800)
- All text is amber (#ffb000)
- Keywords are bold amber
- Comments are dim orange (#cc6600) and italic
- Line numbers are dim orange on dark background

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ide/retro-theme.ts frontend/src/components/ide/editor-pane.tsx
git commit -m "feat(79): add retro-amber Monaco editor theme with phosphor colors"
```

---

## Phase 5: Toolbar and Status Bar

### Task 6: Style toolbar with DOS-style bevel and VT323 font

**Files:**
- Modify: `frontend/src/components/ide/toolbar.tsx`

- [ ] **Step 1: View toolbar.tsx**

Run: `head -100 /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/frontend/src/components/ide/toolbar.tsx`

- [ ] **Step 2: Add toolbar styles**

```css
.toolbar {
  background: #c0c0c0;
  border-top: 2px solid #dfdfdf;
  border-bottom: 2px solid #808080;
  padding: 2px 4px;
  display: flex;
  gap: 4px;
  align-items: center;
  font-family: var(--font-vt323);
  font-size: 12px;
  user-select: none;
}

.toolbar-button {
  background: #c0c0c0;
  border-top: 1px solid #dfdfdf;
  border-right: 1px solid #808080;
  border-bottom: 1px solid #808080;
  border-left: 1px solid #dfdfdf;
  padding: 2px 6px;
  cursor: pointer;
  font-family: var(--font-vt323);
  color: #000;
  active: {
    border-top-color: #808080;
    border-left-color: #808080;
    border-right-color: #dfdfdf;
    border-bottom-color: #dfdfdf;
  }
}

.status-bar {
  background: #0a0800;
  color: var(--retro-fg);
  border-top: 1px solid var(--retro-dim);
  padding: 4px 8px;
  font-family: var(--font-share-tech);
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-bar-segment {
  padding: 0 8px;
  border-right: 1px solid var(--retro-dim);
}
```

- [ ] **Step 3: Update toolbar JSX with DOS styling**

Add className attributes and update button styling:

```tsx
<div className="toolbar">
  {/* buttons with DOS-style borders */}
  <button className="toolbar-button">File</button>
  <button className="toolbar-button">Edit</button>
  <button className="toolbar-button">View</button>
</div>

<div className="status-bar">
  <span className="status-bar-segment">LN {currentLine}, COL {currentCol}</span>
  <span className="status-bar-segment">{fileType}</span>
  <span className="status-bar-segment">UTF-8</span>
</div>
```

- [ ] **Step 4: Test toolbar appearance**

Run: `npm run dev`, verify:
- Toolbar has gray (Windows 95) appearance
- DOS 3D beveled buttons
- VT323 font used in toolbar
- Status bar at bottom with LN/COL, file type, encoding

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ide/toolbar.tsx
git commit -m "feat(79): style toolbar with DOS-style bevel borders, VT323 font, and status bar"
```

---

## Phase 6: Terminal Styling

### Task 7: Apply amber phosphor theme to xterm.js terminal

**Files:**
- Modify: `frontend/src/components/ide/terminal-pane.tsx`

- [ ] **Step 1: View terminal-pane.tsx**

Run: `head -100 /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples/frontend/src/components/ide/terminal-pane.tsx`

- [ ] **Step 2: Add xterm theme configuration**

Add before terminal initialization:

```typescript
const xtermTheme = {
  background: '#0a0800',
  foreground: '#ffb000',
  cursor: '#ffb000',
  cursorAccent: '#0a0800',
  selectionBackground: 'rgba(255, 176, 0, 0.3)',
  black: '#0a0800',
  red: '#ff6b6b',
  green: '#ffb000',
  yellow: '#ff9000',
  blue: '#ffb000',
  magenta: '#ff9000',
  cyan: '#ffb000',
  white: '#ffb000',
  brightBlack: '#cc6600',
  brightRed: '#ff9000',
  brightGreen: '#ffb000',
  brightYellow: '#ffb000',
  brightBlue: '#ffb000',
  brightMagenta: '#ffb000',
  brightCyan: '#ffb000',
  brightWhite: '#ffb000',
};
```

- [ ] **Step 3: Pass theme to Terminal constructor**

Update Terminal initialization:

```typescript
const term = new Terminal({
  theme: xtermTheme,
  fontFamily: 'Share Tech Mono, monospace',
  fontSize: 12,
  lineHeight: 1.2,
  cursorBlink: true,
  cursorStyle: 'block',
});
```

- [ ] **Step 4: Test terminal styling**

Run: `npm run dev`, open terminal in IDE. Verify:
- Terminal background is dark (#0a0800)
- All text is amber (#ffb000)
- Cursor is amber and blinks
- Glow effect visible on text (from existing .phosphor-glow class if applied)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ide/terminal-pane.tsx
git commit -m "feat(79): apply amber phosphor xterm.js theme to terminal pane"
```

---

## Phase 7: Testing and Validation

### Task 8: Visual regression and functional testing

**Files:**
- No code changes (testing phase)

- [ ] **Step 1: Test landing page visuals**

Run: `npm run dev`, navigate to login:
- Dracula theme applied (dark purple background)
- ASCII art SIMPLES logo renders correctly
- Typing animation on title works
- Form has purple borders and glow
- Button hover effect works

- [ ] **Step 2: Test IDE visuals**

Navigate to IDE:
- Dark retro background (#0a0800)
- Amber text (#ffb000) in editor, terminal, toolbar
- Scanlines overlay visible
- Flicker animation subtle but visible
- DOS 3D borders on toolbar
- Status bar shows LN/COL updates as you move cursor

- [ ] **Step 3: Test responsive design**

Resize browser window, verify:
- Landing page centers correctly at all viewport sizes
- IDE layout doesn't break (flex layout maintains)
- Scanlines stay aligned
- Text remains readable

- [ ] **Step 4: Test cross-browser compatibility**

Test in:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest if available)

Verify all theme colors render consistently.

- [ ] **Step 5: No regressions**

Run existing tests:

```bash
npm run test
```

Expected: All tests pass. No breaking changes to existing IDE functionality.

- [ ] **Step 6: Create checkpoint commit (no changes)**

```bash
git add -A
git commit -m "test(79): visual regression and cross-browser validation complete"
```

---

## Phase 8: PR and Merge to Dev

### Task 9: Push feat/79 and create PR

**Files:**
- No code changes (workflow step)

- [ ] **Step 1: Create feat/79 branch (if not done)**

```bash
git checkout -b feat/79
```

- [ ] **Step 2: Verify all commits are present**

```bash
git log --oneline -10
```

Expected: At least 7 commits (fonts, CSS foundation, landing page, IDE effects, Monaco theme, toolbar, terminal).

- [ ] **Step 3: Push feat/79 to origin**

```bash
git push -u origin feat/79
```

- [ ] **Step 4: Create PR**

Using GitHub CLI:

```bash
gh pr create \
  --title "feat(79): complete visual redesign of frontend (Dracula landing + retro IDE)" \
  --body "## Issue #79: Visual Redesign

Implements complete frontend redesign with two themes:
- **Landing Page:** NERD/Dracula aesthetic (dark purple, pink, ASCII art, typing animation)
- **IDE:** Retro 80s/90s phosphor terminal theme (amber on black, scanlines, glow, CRT effects)

### Changes
- Added 4 Google Fonts (JetBrains Mono, Fira Code, VT323, Share Tech Mono)
- New CSS variables for Dracula and Amber Phosphor themes
- Landing page redesign with ASCII art and typing animation
- IDE CRT effects (scanlines overlay, flicker animation, DOS 3D borders)
- Monaco editor retro-amber theme
- Toolbar DOS-style styling with status bar
- xterm.js terminal amber phosphor theme

### Testing
- Visual regression tested (landing + IDE)
- Responsive design verified
- Cross-browser compatibility checked
- All existing tests pass" \
  --base dev \
  --head feat/79
```

- [ ] **Step 5: Wait for review**

Post message in Slack/Discord: "PR #XX ready for review - Issue #79 visual redesign"

- [ ] **Step 6: Merge to dev after approval**

Once review approved:

```bash
gh pr merge --merge --auto
```

Or manually if not using `--auto`:

```bash
git checkout dev
git pull origin dev
git merge feat/79
git push origin dev
```

- [ ] **Step 7: Update PR evidence record**

Edit `pr71.json` or similar evidence tracking file to record merge completion.

---

## Summary

This plan delivers Issue #79 (visual redesign) in 7 atomic commits + testing + PR workflow:

1. Google Fonts + CSS foundation (2 commits)
2. Landing page Dracula theme (1 commit)
3. IDE CRT effects (1 commit)
4. Monaco retro theme (1 commit)
5. Toolbar/status bar DOS styling (1 commit)
6. Terminal amber phosphor (1 commit)
7. Testing validation + PR merge

**Acceptance Criteria (from Issue #79):**
- ✅ Landing page: Dracula theme, NERD aesthetic, ASCII art, typing animation
- ✅ IDE: Retro 80s/90s phosphor theme, amber on black, scanlines, glow, flicker
- ✅ CSS-only animations (no external libraries)
- ✅ Google Fonts loaded (JetBrains Mono, Fira Code, VT323, Share Tech Mono)
- ✅ No regressions (existing IDE functionality preserved)
- ✅ PR workflow followed (feat branch, dev base, review, merge)

**Time estimate:** 2-3 hours implementation + review time

---

## Execution Instructions

Choose one:

**Option 1: Subagent-Driven (Recommended)**
Use `superpowers:subagent-driven-development` to dispatch one task per subagent, review between tasks.

**Option 2: Inline Execution**
Use `superpowers:executing-plans` to batch execute tasks with checkpoints.

