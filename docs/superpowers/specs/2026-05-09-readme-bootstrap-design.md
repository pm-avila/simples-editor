# README Bootstrap Design

## Problema

O repositório ainda não oferece um ponto de entrada útil para quem chega ao projeto. A issue #1 pede um README inicial que explique o que é o Simples Editor, qual stack está prevista, qual é a estrutura mínima do repositório e qual fluxo local de desenvolvimento o projeto adota.

## Escopo aprovado

- Alterar somente `README.md`.
- Tratar o README como o hub inicial de onboarding.
- Referenciar o PRD como fonte de verdade para requisitos e arquitetura.
- Explicar o fluxo local alvo com `docker compose up`, mesmo que a infraestrutura completa ainda esteja sendo consolidada nas issues seguintes da Sprint 1.

## Fora de escopo

- Criar documentação auxiliar nova para setup.
- Descrever arquitetura detalhada além do necessário para onboarding.
- Documentar deploy de produção, fluxo de contribuição ou detalhes de autenticação além de links e contexto.

## Abordagem escolhida

O README será reescrito como uma página curta de bootstrap do projeto, organizada para responder rapidamente quatro perguntas:

1. O que é o Simples Editor.
2. Quais tecnologias principais compõem a solução.
3. Como o repositório está organizado neste estágio inicial.
4. Como o desenvolvimento local deve funcionar usando Docker Compose.

## Estrutura proposta do README

1. Título e resumo objetivo do projeto.
2. Seção "Visão geral" com base no PRD.
3. Seção "Stack planejada" com frontend, backend, proxy, auth e toolchain de execução.
4. Seção "Estrutura atual do repositório" com descrição curta dos diretórios e arquivos já presentes.
5. Seção "Fluxo local de desenvolvimento" explicando pré-requisitos e o comando `docker compose up`.
6. Seção "Fonte de verdade" apontando para `prd-simples-online.md`.
7. Seção curta de status deixando claro que o repositório está em bootstrap de Sprint 1.

## Decisões de conteúdo

- Usar o nome **Simples Editor** de forma explícita logo no topo.
- Assumir um tom de onboarding, não de documentação completa.
- Explicitar que o fluxo local desejado é via Docker Compose para alinhar o README com os critérios da issue e com o PRD.
- Evitar instruções inventadas sobre arquivos ainda inexistentes; quando necessário, usar linguagem de "fluxo adotado/alvo do projeto" em vez de fingir que a infraestrutura já está pronta.

## Verificação

O resultado será considerado pronto quando `README.md`:

- mencionar que o projeto é o Simples Editor;
- descrever objetivo, stack e estrutura mínima;
- apontar o fluxo local baseado em `docker compose up`;
- referenciar o PRD como fonte de verdade.
