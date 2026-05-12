# simples-compiler stub

Este diretório contém um **stub** do compilador `simplesc` para uso em CI e
desenvolvimento antes que a implementação real esteja disponível.

## Como substituir

Coloque os fontes reais do compilador aqui e garanta que o `Makefile`
produza um binário chamado `simplesc` na raiz deste diretório.

## Contrato de invocação

```
simplesc <fonte.simples> -o <saida.asm>
```

- Saída 0 + arquivo `.asm` válido em caso de sucesso.
- Saída 1 + mensagem `<linha>:<coluna>: <mensagem>` no stderr em caso de erro.
