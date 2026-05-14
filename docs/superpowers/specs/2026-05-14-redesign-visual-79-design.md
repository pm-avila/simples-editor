# Design Spec: Issue #79 — Redesign Visual Frontend (Landing + IDE Retro)

**Date:** 2026-05-14  
**Status:** APPROVED  
**Scope:** Landing page (login) com estilo NERD + IDE com estilo retro 80s/90s

---

## 1. Visão Geral

O **Simples Editor** é um projeto educacional para compiladores. Atualmente a UI é genérica (VSCode-like). Este redesign consolida a identidade visual do projeto em dois eixos:

1. **Página de login** → Estilo NERD moderno (Dracula), impactante e geek
2. **Página do editor** → Estilo retro terminal 80s/90s (fósforo), nostálgico e funcional

A implementação usa **CSS puro** (sem bibliotecas de animação), preserva acessibilidade, e segue patterns React já estabelecidos no codebase.

---

## 2. Página de Login — Estilo NERD/Dracula

### 2.1 Arquitetura

**Componentes afetados:**
- `frontend/src/components/auth/login-screen.tsx` (redesign visual + animações)
- `frontend/index.html` (Google Fonts link)
- `frontend/src/styles.css` (variáveis Dracula, estilos base)

**Paleta de cores — Dracula:**

| Token | Hex | Uso |
|---|---|---|
| Background | `#282a36` | Fundo da página |
| Current line | `#44475a` | Cards, inputs, hover |
| Purple | `#bd93f9` | Títulos, destaque primário |
| Pink | `#ff79c6` | Hover, acento secundário |
| Cyan | `#8be9fd` | Labels, subtítulos |
| Green | `#50fa7b` | Botão login, sucesso |
| Orange | `#ffb86c` | Avisos, atenção |
| Red | `#ff5555` | Erros |
| Foreground | `#f8f8f2` | Texto principal |

**Tipografia:**
- **Logo/Título:** JetBrains Mono Bold 800 (Google Fonts, ligatures)
- **Subtítulo/Corpo:** Fira Code Regular 400 (Google Fonts, ligatures)

### 2.2 Elementos Visuais

1. **ASCII Art do Logo**
   - Renderizado em `<pre>` com fonte JetBrains Mono
   - Cor: `#bd93f9` (purple)
   - Localização: Acima do formulário
   - Conteúdo: 6 linhas (spec na issue #79)

2. **Typing Animation**
   - CSS `@keyframes` com `steps()` (simula typing)
   - Subtítulo: `> Compilador educacional para SIMPLES — IFSULDEMINAS`
   - Cursor piscante: `█` (U+2588) ou `|`
   - Duração: ~2–3s + loop infinito do cursor
   - Sem JavaScript adicional

3. **Formulário de Login**
   - Inputs: borda `#44475a`, glow `#bd93f9` no focus, fundo `#282a36`
   - Labels: cor `#8be9fd` (cyan), fonte Fira Code
   - Botão "Sign In": background `#50fa7b`, texto `#282a36`, hover com leve scale CSS
   - Mensagem de erro: `#ff5555` (red)

4. **Badge Institucional**
   - Posição: Abaixo do formulário
   - Texto: 2 linhas (emoji + texto)
   - Cor: `#8be9fd` (cyan), pequeno tamanho
   - Conteúdo: "🎓 Projeto educacional... | Prof. Paulo Muniz de Ávila"

5. **Background**
   - Cor base: `#282a36`
   - Grade de pontos via `radial-gradient` CSS
   - Opacidade: Sutil, ~5–10%

### 2.3 Acessibilidade & Responsividade

- Labels + `for` attributes (associação ARIA)
- Contrast ratio: WCAG AA (Purple `#bd93f9` em fundo `#282a36` → ~6:1)
- Tab order mantido
- Responsive: 1024px, 1440px, 1920px (mobile pode ficar para sprint futura)

---

## 3. Página do Editor — Estilo Retro 80s/90s

### 3.1 Arquitetura

**Componentes afetados:**
- `frontend/src/components/ide/ide-shell.tsx` (scanlines, flicker, container CRT)
- `frontend/src/components/ide/toolbar.tsx` (estilo bevel DOS, labels VT323)
- `frontend/src/components/ide/terminal-pane.tsx` (tema xterm âmbar)
- `frontend/src/components/ide/retro-theme.ts` (NEW — tema Monaco retro)
- `frontend/index.html` (Google Fonts VT323 + Share Tech Mono)
- `frontend/src/styles.css` (variáveis retro, efeitos CRT)

**Paleta de cores — Fósforo Âmbar:**

| Token | Hex | Uso |
|---|---|---|
| Background | `#0a0800` | Fundo tela |
| Foreground | `#ffb000` | Texto principal |
| Bright | `#ffd700` | Títulos, labels ativos |
| Dim | `#7a5800` | Texto inativo, bordas |
| Error | `#ff4400` | Mensagens erro |

**Variante alternativa:** Verde fósforo (`#001a00` bg / `#33ff33` fg) via CSS custom property (não vai na V1, fica para futuro).

**Tipografia:**
- **Labels/Headers:** VT323 (Google Fonts — criada para imitar terminais CRT)
- **Código/Terminal:** Share Tech Mono (Google Fonts)

### 3.2 Efeitos CSS

Todos implementados em **CSS puro**, sem JavaScript:

1. **Scanlines (overlay)**
   ```css
   .ide-crt::after {
     content: '';
     position: fixed; inset: 0; pointer-events: none; z-index: 9999;
     background: repeating-linear-gradient(
       0deg, transparent, transparent 2px,
       rgba(0,0,0,0.15) 2px, rgba(0,0,0,0.15) 4px
     );
   }
   ```

2. **Phosphor Glow (text-shadow)**
   ```css
   .crt-text {
     text-shadow: 0 0 8px #ffb000, 0 0 16px rgba(255,176,0,0.5);
   }
   ```

3. **Screen Flicker (animation)**
   ```css
   @keyframes flicker {
     0%, 100% { opacity: 1.0; }
     92% { opacity: 0.97; }
     94% { opacity: 1.0; }
     96% { opacity: 0.98; }
   }
   .ide-crt { animation: flicker 8s infinite; }
   ```

4. **Monitor Border (box-shadow)**
   ```css
   .ide-crt {
     border-radius: 12px;
     box-shadow: 0 0 40px rgba(255,176,0,0.2) inset,
                 0 0 80px rgba(255,176,0,0.07);
   }
   ```

### 3.3 Monaco Editor — Tema Retro

Arquivo novo: `frontend/src/components/ide/retro-theme.ts`

Tokens de cor:
- **Background:** `#0a0800`
- **Keywords:** `#ffd700` (bold)
- **Strings:** `#ffaa00`
- **Comments:** `#7a5800` (itálico)
- **Numbers:** `#ff8800`
- **Operators:** `#ffcc00`
- **Line numbers:** `#7a5800`
- **Cursor:** `#ffd700`

### 3.4 Toolbar & Status Bar

**Toolbar:**
- Font: VT323
- Botões: Estilo bevel DOS (border claro em top/left, escuro em bottom/right)
- Spacing: 8px padding

**Status Bar (nova, fixa no bottom):**
- Formato: `[SIMPLES]  [PRONTO]  [LN: 1  COL: 1]  [IFSULDEMINAS]`
- Font: VT323
- Background: `#0a0800`, Foreground: `#ffb000`
- Height: 24px
- Atualizar LN/COL em tempo real quando editor muda

**Botões Run/Stop:**
- Run: `[▶ EXECUTAR]`
- Stop: `[■ PARAR]`
- Estilo: bevel DOS, labels em CAPS

### 3.5 Terminal xterm.js

Configuração de tema no `TerminalPane`:
```typescript
theme: {
  background: '#0a0800',
  foreground: '#ffb000',
  cursor: '#ffd700',
  cursorAccent: '#0a0800',
  selectionBackground: 'rgba(255,176,0,0.3)',
}
```

---

## 4. Critérios de Aceitação

### Landing Page
- [ ] Google Fonts (JetBrains Mono + Fira Code) carregadas e funcional
- [ ] ASCII art do logo renderizado com JetBrains Mono, cor purple
- [ ] Typing animation CSS no subtítulo com cursor piscante
- [ ] Paleta Dracula aplicada em todos elementos (inputs, labels, botão, fundo)
- [ ] Badge IFSULDEMINAS visível abaixo do formulário
- [ ] Acessibilidade mantida (labels, tab order, contrast)
- [ ] Responsivo em 1024px e 1920px
- [ ] Login ainda funciona end-to-end (token, redirecionamento)

### IDE
- [ ] Google Fonts (VT323 + Share Tech Mono) carregadas
- [ ] Scanlines overlay CSS aplicado e visível
- [ ] Phosphor glow (text-shadow âmbar) em textos
- [ ] Flicker animation sutil (8s loop)
- [ ] Tema Monaco retro exportado e aplicado ao editor
- [ ] Terminal xterm com tema âmbar
- [ ] Status bar inferior estilo DOS visível
- [ ] Botões Run/Stop com labels retro
- [ ] IDE mantém toda funcionalidade anterior (edit, run, stop, stdin, timeout)

### Geral
- [ ] Sem novas dependências npm (CSS puro, tipografia Google Fonts)
- [ ] Commits atomizados: landing, IDE, tema Monaco
- [ ] Testes visuais validados (screenshots ou demo ao vivo)
- [ ] PR comentada com referência a efeitos e paletas

---

## 5. Implementação — Ordem Recomendada

1. **CSS Base** — Google Fonts, variáveis Dracula/Retro, utilidades
2. **Landing Page** — ASCII art + typing animation + formulário Dracula
3. **IDE Efeitos** — Scanlines, glow, flicker em styles.css
4. **Tema Monaco** — retro-theme.ts
5. **Toolbar/Status Bar** — Bevel estilo DOS, labels VT323
6. **Terminal xterm** — Tema âmbar
7. **Testes visuais** — Validar contrast, responsividade, acessibilidade
8. **PR & Review** — Documentar efeitos, screenshots, paletas

---

## 6. Fora do Escopo (Sprint Futura)

- Bibliotecas de animação externas (Framer Motion, GSAP)
- Mudanças de lógica de autenticação
- Endpoints de backend
- Tela de cadastro
- Suporte mobile (responsive em tablets +)
- Tema verde fósforo alternativo

---

## 7. Referências da Spec

- [Issue #79 — GitHub](https://github.com/pm-avila/simples-editor/issues/79)
- [Dracula Theme](https://draculatheme.com/)
- [Cool Retro Term](https://github.com/Swordfish90/cool-retro-term)
- [VT323 Font](https://fonts.google.com/specimen/VT323)
- [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono)
- [ASCII Art — TAAG](https://patorjk.com/software/taag/)

---

## 8. Design Review Checklist

- [x] Escopo bem definido e isolado
- [x] Paletas de cor especificadas (WCAG AA)
- [x] Tipografia (Google Fonts) sem dependências extras
- [x] Efeitos CSS (scanlines, glow, flicker) viáveis em CSS puro
- [x] Acessibilidade mantida
- [x] Componentes existentes reutilizados (nenhum novo componente, só estilos)
- [x] Critérios de aceitação mensuráveis
- [x] Compatibilidade com fluxo anterior (auth, IDE, terminal)

**Pronto para implementação.**
