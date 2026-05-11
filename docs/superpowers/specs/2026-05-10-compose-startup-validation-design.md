# Docker Compose Startup Validation Design

## Problema

A issue #4 exige mais do que a existência do `docker-compose.yml`: o ambiente precisa subir em fluxo limpo e responder em `http://localhost`. Como a `dev` ainda não contém o scaffold da issue #3, a branch da issue #4 precisa ser autocontida para validar a subida real do ambiente.

## Escopo aprovado automaticamente

- Tornar a branch `feat/4` autocontida com a fundação do compose necessária para a validação local.
- Garantir que `docker compose up --build` consiga subir os serviços sem ajustes manuais fora do fluxo documentado.
- Garantir que a página inicial responda via `nginx` em `http://localhost`.
- Atualizar a documentação apenas no que for necessário para refletir o fluxo real de validação local.

## Fora de escopo

- Implementar autenticação Supabase real.
- Entregar login funcional.
- Adicionar pipeline de compilação, sandbox real ou backend final.
- Introduzir testes E2E pesados ou infraestrutura de CI nova para Docker.

## Abordagens consideradas

### 1. Reimplementar tudo dentro da issue #4

Reconstruir compose, serviços e validação sem reaproveitar o trabalho da issue #3.

**Vantagens**
- Branch totalmente independente.

**Desvantagens**
- Duplica esforço.
- Aumenta chance de divergência entre #3 e #4.

### 2. Basear a issue #4 na fundação da `feat/3` e acrescentar validação (**escolhida**)

Trazer para `feat/4` os artefatos da fundação do compose e, sobre eles, adicionar os ajustes mínimos para que o ambiente suba e responda em `http://localhost`.

**Vantagens**
- Mantém continuidade entre #3 e #4.
- Faz da #4 uma branch autocontida em relação à `dev`.
- Minimiza retrabalho e reduz inconsistência arquitetural.

**Desvantagens**
- A branch incorpora mudanças que também existem na #3, exigindo atenção na integração posterior.

### 3. Validar apenas por inspeção estrutural

Criar testes de contrato e atualizar README sem realmente subir o ambiente.

**Vantagens**
- Menor custo de implementação.

**Desvantagens**
- Não atende o aceite principal da issue, que pede `docker compose up` funcionando.

## Arquitetura escolhida

### Estratégia

1. Reaproveitar a fundação do compose da issue #3 na branch `feat/4`.
2. Verificar o fluxo real de `docker compose up --build`.
3. Ajustar apenas o que impedir a subida limpa dos três serviços.
4. Adicionar uma verificação automatizada leve para o contrato operacional:
   - serviços sobem;
   - `nginx` responde em `http://localhost`;
   - o fluxo documentado do README bate com o comportamento real.

### Componentes

- `docker-compose.yml`
- `frontend/`
- `backend/`
- `nginx/default.conf`
- `README.md`
- teste/validação local automatizada para startup

## Decisões de implementação

- A branch `feat/4` pode incorporar os commits de fundação da `feat/3`, porque `dev` ainda não os tem e a validação depende deles.
- O critério principal de validação será `docker compose up --build` seguido de checagem HTTP em `http://localhost`.
- O backend continua mínimo; o foco é operacional, não funcional além do necessário para a resposta do ambiente.
- O `nginx` permanece como único ponto de entrada exposto ao host.

## Tratamento de erros

- Ajustes devem priorizar falhas reais observadas ao subir os containers.
- Se algum serviço depender de configuração opcional, devem existir defaults seguros para ambiente local.
- A documentação deve refletir exatamente os passos necessários, sem pré-requisitos implícitos além de Docker e Compose.

## Verificação

O resultado estará pronto quando:

- `docker compose up --build` subir os serviços necessários sem ajuste manual extra;
- `http://localhost` responder com a página inicial;
- o fluxo descrito no README refletir os passos reais usados na validação.
