# Design: xterm.js no painel de terminal (Issue #25)

## Problema

O painel inferior ainda é um placeholder estático e não suporta stream incremental nem entrada interativa. A issue #25 exige integração real com xterm.js mantendo o layout existente.

## Abordagens avaliadas

1. **Componente React com `xterm` + `xterm-addon-fit` (recomendada)**  
   Cria uma camada de terminal encapsulada com ciclo de vida controlado por `useEffect`, mantendo o restante da IDE desacoplado.

2. **Instanciar xterm diretamente em `IdeShell`**  
   Menos arquivos, mas mistura responsabilidades de layout, execução e terminal em um único componente.

3. **Mock terminal (textarea) temporário**  
   Entrega parcial, mas não atende o critério de aceite de usar xterm.js.

## Recomendação

Adotar a abordagem 1: um `TerminalPane` com `forwardRef` para API mínima (`write`, `clear`, `focus`, `onData`). Isso permite integração progressiva com WebSocket sem alterar contratos externos da UI.

## Arquitetura proposta

```
frontend/src/components/ide/
├── terminal-pane.tsx          ← integra xterm.js + fit addon
└── ide-shell.tsx              ← conecta terminal à orquestração de run

frontend/src/styles.css        ← ajustes visuais do host do terminal
frontend/package.json          ← dependências xterm + xterm-addon-fit
```

## Fluxo de dados

1. `TerminalPane` monta instância `Terminal` ao montar componente.
2. `FitAddon` ajusta o terminal ao container.
3. `IdeShell` escreve mensagens de status/saída via ref.
4. Dados digitados no terminal são encaminhados por callback para camada de execução.

## Erros e robustez

- Se container não tiver tamanho na primeira renderização, chamar `fit()` em `requestAnimationFrame`.
- Limpar listeners e `dispose()` ao desmontar para evitar vazamento.
- Não derrubar UI em exceções de escrita: descartar chunk inválido e continuar sessão.

## Testes

- Testes estáticos/contratuais cobrindo:
  - import de `xterm` e `xterm-addon-fit`
  - existência do host DOM do terminal
  - API de integração (`onData`/ref) presente no componente

## Mapeamento de aceite (Issue #25)

| Critério | Implementação |
|---|---|
| Painel inferior usa xterm.js | `TerminalPane` com `new Terminal()` |
| Renderiza saída incremental | método `write()` exposto por ref |
| Respeita layout e estados visuais | estilos do host + integração em `IdeShell` |
