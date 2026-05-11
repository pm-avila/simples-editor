# Sprint 1 Kanban Automation Design

## Problema

A issue #2 pede um fluxo operacional único para acompanhar backlog, execução e revisão no GitHub Project. O repositório já possui um Project v2 com colunas de status e as issues da Sprint 1 já aparecem nele, mas ainda falta transformar esse quadro em um fluxo automatizado, reproduzível e versionado no próprio repositório.

Além disso, o processo solicitado para a Sprint 1 depende de uma esteira previsível: abrir branch por issue, criar PR contra `dev`, refletir andamento no Project e manter um resumo humano em `PROGRESS.md`.

## Objetivo

Entregar uma automação versionada no repositório para que:

1. issues elegíveis da Sprint 1 entrem no GitHub Project automaticamente;
2. o campo `Status` do Project acompanhe o ciclo `Backlog -> In progress -> In review -> Done`;
3. o fluxo branch/PR contra `dev` seja o caminho padrão do time;
4. `PROGRESS.md` reflita o estado atual das issues da Sprint 1.

## Escopo aprovado automaticamente

- Configurar automação no repositório para integrar issues e pull requests ao GitHub Project existente (`pm-avila` Project 2).
- Versionar a lógica de sincronização no repositório usando GitHub Actions e script de apoio.
- Atualizar `PROGRESS.md` como visão resumida da Sprint 1.
- Documentar como o fluxo opera e quais convenções ele assume.

## Fora de escopo

- Criar um novo GitHub Project.
- Automatizar merge de pull requests.
- Reescrever o backlog inteiro fora da Sprint 1.
- Implementar as demais features das issues #3 em diante nesta mesma entrega.

## Abordagens consideradas

### 1. Configuração apenas manual no GitHub Project

Usar somente automações nativas do Project e ajustes manuais no site do GitHub.

**Vantagens**
- Mais rápida para ativar.
- Não exige código novo no repositório.

**Desvantagens**
- Difícil de auditar e reproduzir.
- Fica dependente de configuração fora do versionamento.
- Não resolve o pedido de fluxo automatizado fim a fim.

### 2. GitHub Actions + script versionado no repositório (**escolhida**)

Usar workflows do GitHub Actions para reagir a eventos de `issues` e `pull_request`, com um script idempotente responsável por localizar o item no Project e atualizar o campo `Status`.

**Vantagens**
- Automação auditável e reproduzível.
- Funciona com o fluxo real de issue -> branch -> PR -> merge.
- Mantém a lógica crítica sob versionamento.

**Desvantagens**
- Exige configurar secrets/variables do repositório para o Project.
- Precisa lidar com chamadas GraphQL do GitHub Project v2.

### 3. Script local executado manualmente via `gh`

Criar um comando local que o time roda ao abrir branch, abrir PR e fechar issue.

**Vantagens**
- Simples de desenvolver.
- Reaproveita o `gh` já presente no fluxo do time.

**Desvantagens**
- Não é automático de verdade.
- Depende de disciplina manual do operador.
- Tem mais chance de divergência entre GitHub e `PROGRESS.md`.

## Arquitetura escolhida

### Componentes

1. **Workflow de sincronização do Project**
   - Disparado por eventos de `issues` e `pull_request`.
   - Decide qual status aplicar ao item do Project.

2. **Script de atualização do Project**
   - Recebe número da issue, ação do evento e metadados do PR.
   - Usa GitHub GraphQL para localizar o item correspondente no Project 2 do usuário `pm-avila`.
   - Atualiza o campo `Status` com valores já existentes no projeto.

3. **Workflow/manual command para `PROGRESS.md`**
   - Consulta issues abertas/fechadas da Sprint 1.
   - Reescreve o arquivo de progresso em formato estável.

4. **Documentação enxuta**
   - Explica as secrets/variables esperadas.
   - Define a convenção de branch `feat/<issue-number>` e PR com base `dev`.

### Fluxo de estados

1. **Issue aberta ou rotulada para Sprint 1** -> garantir presença no Project com `Backlog`.
2. **PR aberto ou reaberto referenciando a issue** -> mover para `In progress` ou `In review`.
3. **PR marcado pronto para revisão / review solicitado** -> `In review`.
4. **Issue fechada ou PR mergeado com fechamento da issue** -> `Done`.

Para reduzir ambiguidade, a automação usará esta regra:

- `Backlog`: issue aberta sem PR associado.
- `In progress`: existe PR aberto associado, mas ainda é draft.
- `In review`: existe PR aberto associado e não está em draft.
- `Done`: issue fechada.

## Convenções operacionais

- Branch de trabalho: `feat/<issue-number>`.
- Base de PR: sempre `dev`.
- As issues elegíveis são as da milestone `Sprint 1` ou com label `sprint-1`.
- O Project alvo é o **Project 2 de `pm-avila`**, já existente.
- O script deve ser idempotente: rodar mais de uma vez não pode criar duplicidade nem falhar por item já sincronizado.

## Tratamento de erros

- Se a issue não pertencer à Sprint 1, o workflow encerra sem erro.
- Se o item não existir no Project, a automação tenta adicioná-lo antes de atualizar o status.
- Se faltar configuração obrigatória do Project no repositório, o workflow falha explicitamente com mensagem clara.
- Se a API do GitHub retornar item ou campo inesperado, o script encerra com erro em vez de aplicar fallback silencioso.

## Testabilidade

- Testar localmente o script com fixtures JSON e casos de mapeamento de estado.
- Validar sintaxe dos workflows.
- Executar o script em modo dry-run para uma issue da Sprint 1.
- Verificar que `PROGRESS.md` é gerado a partir do estado real das issues.

## Entrega esperada

Esta issue estará pronta quando o repositório contiver:

- workflow(s) versionados para sincronização com o GitHub Project;
- script de apoio para atualizar/adicionar itens e status;
- `PROGRESS.md` inicial gerado a partir da Sprint 1;
- documentação curta explicando a configuração e o fluxo branch/PR.
