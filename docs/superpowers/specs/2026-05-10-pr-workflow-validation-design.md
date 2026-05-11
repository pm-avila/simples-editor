# PR Workflow Validation Design

## Problema

A Sprint 1 pede evidência de que o time consegue trabalhar em paralelo com branch, revisão e merge sem travar o fluxo. Hoje o repositório mostra PRs abertos para as issues da sprint, mas não traz uma fonte de verdade versionada para a lista de integrantes, nem prova que cada integrante já teve pelo menos um PR mergeado.

## Assunção operacional

Como o usuário não está disponível e não há uma lista explícita de integrantes no repositório, a melhor base de desenho é assumir que a validação precisa ser **auditável e versionada**. Isso exige dois insumos concretos:

1. uma lista explícita dos integrantes do time no repositório;
2. um registro verificável de PRs mergeados por integrante.

Sem esses dois insumos, não dá para afirmar honestamente que o critério de aceite já foi cumprido.

## Escopo aprovado

- Definir um fluxo versionado para validar participação de cada integrante em pelo menos um PR mergeado.
- Cobrir abertura de branch, revisão e merge no processo documentado.
- Alinhar o fluxo com o objetivo de trabalho paralelo da Sprint 1.
- Manter a solução focada em documentação operacional e evidência auditável.

## Fora de escopo

- Inventar nomes de integrantes ou inferir equipe a partir de um único autor de PR.
- Marcar a issue como concluída sem PRs efetivamente mergeados.
- Automatizar merge de PRs ou reescrever histórico do repositório.

## Abordagens consideradas

### 1. Checklist textual no README

Adicionar apenas um checklist explicando como o time deve abrir, revisar e mesclar PRs. É o caminho mais simples, mas não oferece prova auditável de que cada integrante realmente participou.

### 2. Fluxo documentado + roster versionado + evidência de PRs mergeados (**escolhida**)

Versionar um artefato curto com a lista de integrantes e um registro objetivo de PRs mergeados por pessoa, junto com o fluxo operacional esperado. É a melhor opção porque transforma o critério de aceite em algo verificável dentro do repositório, sem depender de memória ou interpretação.

### 3. Auditoria puramente automática via GitHub API

Criar uma checagem que leia PRs mergeados diretamente do GitHub e derive a participação do time. Isso reduz trabalho manual, mas continua precisando de uma lista explícita de integrantes para comparar e amplia o escopo técnico para uma issue marcada como `docs`.

## Desenho escolhido

A issue deve produzir uma pequena trilha documental composta por:

- um documento de fluxo explicando branch, PR, revisão e merge;
- um roster versionado com os integrantes esperados;
- um quadro simples de evidência ligando cada integrante a pelo menos um PR mergeado.

Essa combinação cobre o processo e também a prova do resultado.

## Estrutura proposta

- `docs/pr-workflow.md` descreve o fluxo mínimo: sair de `dev`, criar `feat/X`, abrir PR contra `dev`, revisar, mesclar e atualizar a evidência.
- `docs/team-roster.md` lista explicitamente os integrantes que precisam cumprir o critério.
- `docs/pr-evidence.md` registra, para cada integrante, ao menos um PR mergeado com link.
- `README.md` pode receber um link curto para esses artefatos, se isso ajudar o onboarding.

## Critério de validação

A issue só pode ser considerada concluída quando:

- `docs/team-roster.md` tiver a lista real de integrantes;
- `docs/pr-evidence.md` mostrar ao menos um PR mergeado por integrante;
- o fluxo documentado cobrir branch, revisão e merge;
- as evidências apontarem para PRs realmente mergeados.

## Bloqueio atual

No estado atual da sessão, esse critério ainda não pode ser fechado honestamente porque:

- não existe lista explícita dos integrantes no repositório;
- os PRs recentes da Sprint 1 estão abertos, não mergeados;
- o histórico visível aponta essencialmente para um único autor.

## Verificação

Quando os insumos existirem, a validação final deve ser objetiva:

1. conferir a lista em `docs/team-roster.md`;
2. conferir um PR mergeado por integrante em `docs/pr-evidence.md`;
3. verificar que cada evidência aponta para merge real contra `dev`;
4. confirmar que o fluxo documentado continua alinhado ao trabalho paralelo da Sprint 1.
