# Docker Compose Foundation Design

## Problema

A issue #3 pede a fundação do ambiente local do projeto. Hoje o repositório não tem `docker-compose.yml`, nem containers base para proxy, frontend e backend. Sem esse contrato operacional, o time não consegue convergir na topologia do ambiente nem preparar a validação do `docker compose up` da issue seguinte.

## Escopo aprovado automaticamente

- Criar `docker-compose.yml` para três serviços: `nginx`, `frontend` e `backend`.
- Adicionar os artefatos mínimos para cada serviço existir de forma coerente no repositório.
- Mapear no compose as variáveis relevantes para Supabase, timeouts e imagem de sandbox.
- Seguir uma topologia simples: `nginx` exposto para o host, `frontend` e `backend` acessíveis apenas na rede interna.

## Fora de escopo

- Concluir autenticação Supabase.
- Implementar a tela de login.
- Entregar o comportamento validado de `docker compose up` em `http://localhost` como aceite formal da issue #4.
- Adicionar pipeline de compilação, sandbox real ou endpoints além do mínimo para o esqueleto do backend.

## Abordagens consideradas

### 1. Compose sem serviços reais

Criar apenas `docker-compose.yml` apontando para imagens genéricas, sem diretórios próprios do frontend/backend.

**Vantagens**
- Menor volume de arquivos.
- Resolve o contrato superficialmente.

**Desvantagens**
- Fraco como base para a issue #4.
- Não deixa clara a responsabilidade de cada serviço.
- Cria retrabalho imediato no próximo passo.

### 2. Scaffold funcional mínimo com três serviços (**escolhida**)

Criar o compose e um esqueleto pequeno para `nginx`, `frontend` e `backend`, já com Dockerfiles e arquivos mínimos de execução.

**Vantagens**
- Entrega o contrato e também prepara o próximo passo da Sprint 1.
- Mantém o escopo pequeno, mas com artefatos reais.
- Facilita evolução incremental sem trocar a topologia.

**Desvantagens**
- Cria mais arquivos agora.
- Exige definir uma convenção inicial de estrutura de diretórios.

### 3. Compose já validado para localhost completo

Entregar desde já tudo que a issue #4 precisa, incluindo página inicial confirmada.

**Vantagens**
- Menos retrabalho entre #3 e #4.

**Desvantagens**
- Invade explicitamente o escopo da issue #4.
- Mistura scaffold com validação operacional.

## Arquitetura escolhida

### Estrutura

1. `docker-compose.yml`
   - serviço `nginx`
   - serviço `frontend`
   - serviço `backend`
   - rede interna única
   - volumes somente onde fizer sentido para desenvolvimento

2. `frontend/`
   - `Dockerfile`
   - aplicação mínima servida em porta interna
   - arquivo inicial simples o suficiente para provar a existência do serviço

3. `backend/`
   - `Dockerfile`
   - app Flask mínima
   - endpoint básico de esqueleto, sem ainda assumir o `/api/health` da issue #8 como entrega formal

4. `nginx/`
   - configuração para publicar a porta HTTP
   - proxy para frontend na raiz
   - rota `/api/` encaminhada ao backend

5. `.env.example`
   - placeholders para URL/chaves do Supabase
   - timeout de compilação
   - timeout de execução
   - imagem de sandbox

### Topologia

- `nginx` expõe `80:80`.
- `frontend` roda apenas na rede Docker interna.
- `backend` roda apenas na rede Docker interna.
- `nginx` faz proxy:
  - `/` -> `frontend`
  - `/api/` -> `backend`

Essa topologia mantém o desenho arquitetural básico descrito pela Sprint 1 e evita acoplar o host diretamente aos serviços internos.

## Convenções e conteúdo mínimo

- O frontend pode ser um servidor HTTP mínimo servindo um HTML estático inicial; não precisa ser um scaffold React completo nesta issue.
- O backend deve usar Flask, já alinhado ao stack descrito nas issues da Sprint.
- O compose deve carregar variáveis de ambiente a partir de `.env` quando presente, mas o repositório deve versionar apenas `.env.example`.
- A composição deve declarar explicitamente as variáveis de Supabase, timeouts e sandbox, mesmo que algumas ainda não sejam consumidas pela aplicação.

## Tratamento de erros

- Nenhum serviço deve depender de valores secretos reais para o container subir em modo scaffold.
- Valores ausentes devem usar placeholders/defaults seguros no compose.
- A documentação deve deixar claro que as variáveis reais serão preenchidas nas issues de autenticação e runtime.

## Verificação

O resultado estará pronto quando:

- existir `docker-compose.yml` com `nginx`, `frontend` e `backend`;
- a composição expuser variáveis de Supabase, timeouts e imagem de sandbox;
- a estrutura mínima dos três serviços estiver presente no repositório;
- a topologia estiver coerente com proxy externo e serviços internos.
