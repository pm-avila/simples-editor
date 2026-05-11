# Public Health Check Design

## Problema

A Sprint 1 precisa de um endpoint de health check publico para validar rapidamente se o backend esta de pe em ambiente local e, depois, no deploy. A branch `dev` ainda esta quase vazia, entao a issue #8 precisa ser autocontida o suficiente para expor `GET /api/health` sem depender de merges anteriores.

## Escopo aprovado

- Criar uma fundacao backend minima na branch `feat/8`.
- Expor `GET /api/health` sem exigir JWT.
- Retornar pelo menos o estado geral do servico em JSON.
- Cobrir o contrato com testes automatizados reais do backend.
- Documentar o contrato minimo no `README.md`.

## Fora de escopo

- Integrar Docker Compose, nginx ou frontend nesta issue.
- Reaplicar a fundacao completa de auth da issue #7.
- Adicionar checks profundos de banco, Supabase ou dependencias externas.
- Criar endpoints protegidos ou middleware global de autenticacao.

## Abordagens consideradas

### 1. Backend Flask minimo e autocontido (**escolhida**)

Criar um app Flask pequeno com um endpoint publico `GET /api/health`, um helper isolado para o payload do health check e testes via Flask test client. E a melhor opcao porque atende exatamente a issue, mantem a branch pequena e reduz acoplamento com artefatos que ainda nao chegaram em `dev`.

### 2. Reaplicar toda a fundacao backend+auth antes do health check

Trazer tambem o modulo de JWT da issue #7 e ja estruturar endpoints publicos e protegidos. Isso aproxima a branch de um backend mais completo, mas expande escopo sem necessidade para esta issue e aumenta custo de manutencao numa `dev` ainda minima.

### 3. Endpoint estrutural sem framework HTTP real

Limitar a entrega a funcoes e testes estruturais de arquivo, adiando um servidor HTTP real para depois. Isso seria mais barato no curtissimo prazo, mas nao prova o contrato `GET /api/health` de forma confiavel.

## Arquitetura escolhida

A branch passa a ter um backend Flask pequeno e focado:

- `backend/app.py` contem o app Flask e registra `GET /api/health`.
- `backend/health.py` centraliza a montagem do payload para manter a rota simples e facilitar evolucao futura.
- `backend/requirements.txt` declara Flask explicitamente.
- `backend/__init__.py` marca o pacote.
- `tests/test_health_endpoint.py` valida arquivos obrigatorios, contrato HTTP do endpoint e documentacao.
- `README.md` descreve como validar o health check localmente.

## Contrato do endpoint

- Metodo: `GET`
- Rota: `/api/health`
- Autenticacao: nenhuma
- Resposta: JSON com pelo menos `status`
- Valor esperado de sucesso: `{"status": "ok"}`

Para deixar o contrato um pouco mais util sem sair do escopo, o payload tambem pode incluir um identificador simples do servico, desde que `status: "ok"` continue presente e estavel.

## Fluxo de dados

1. O cliente chama `GET /api/health`.
2. A rota Flask delega a construcao do payload a um helper pequeno.
3. O backend responde JSON 200 sem consultar dependencias externas.

## Tratamento de erros

Como o endpoint e deliberadamente superficial, nao deve falhar por ausencia de banco ou auth. O comportamento esperado nesta issue e sempre responder o estado basico do processo local. Se no futuro houver checks aprofundados, eles devem ser adicionados sem quebrar o contrato minimo `status: "ok"` para o modo saudavel.

## Estrategia de testes

Os testes devem seguir TDD e cobrir:

- existencia dos arquivos minimos do backend;
- resposta 200 em `GET /api/health`;
- payload JSON contendo pelo menos `status: "ok"`;
- ausencia de qualquer exigencia de JWT para esse endpoint;
- documentacao do contrato no `README.md`.

## Verificacao

A issue sera considerada pronta quando a branch `feat/8`:

- expuser `GET /api/health` via Flask test client;
- retornar JSON com `status: "ok"`;
- mantiver o endpoint publico;
- documentar o health check no `README.md`.
