# Supabase Login Design

## Problema

A issue #6 pede um fluxo mínimo de login no frontend usando email e senha com o cliente do Supabase, liberando acesso à IDE após autenticação. A branch `dev`, porém, ainda está quase vazia, então a solução precisa ser autocontida e pequena o bastante para não introduzir uma stack inteira de frontend antes da hora.

## Escopo aprovado

- Tornar a branch `feat/6` autocontida para um fluxo mínimo de login.
- Criar uma tela de login com campos de email e senha.
- Usar explicitamente o cliente JavaScript do Supabase para autenticação por email/senha.
- Liberar uma área mínima de “IDE” após existir sessão válida.
- Reusar o contrato de auth do v1 com `SUPABASE_URL` e `SUPABASE_ANON_KEY`.
- Cobrir o contrato com testes reprodutíveis sem exigir browser automation.

## Fora de escopo

- Migrar já para React/Vite.
- Implementar registro, recuperação de senha ou logout sofisticado.
- Validar JWT no backend; isso fica para a issue #7.
- Criar a IDE real; nesta issue basta uma shell protegida.

## Abordagens consideradas

### 1. Frontend estático com módulos JS e cliente Supabase (**escolhida**)

Pró: menor superfície, branch autocontida, sem toolchain novo.  
Contra: não entrega ainda a base React prevista mais à frente.

### 2. Scaffold React/Vite com login já nessa issue

Pró: aproxima o repositório do alvo de médio prazo.  
Contra: aumenta muito o escopo para uma `dev` ainda sem fundação frontend.

### 3. Mockar login sem cliente Supabase real

Pró: implementação barata.  
Contra: não atende o critério central da issue.

## Abordagem escolhida

A solução será um frontend estático mínimo com três arquivos:

1. `frontend/index.html` para a UI;
2. `frontend/config.js` para centralizar `SUPABASE_URL` e `SUPABASE_ANON_KEY`;
3. `frontend/app.js` para inicializar o cliente Supabase, executar `signInWithPassword`, restaurar sessão e alternar entre a tela de login e uma shell protegida da IDE.

## Estrutura proposta

- `frontend/index.html` — formulário de login e shell protegida.
- `frontend/config.js` — contrato mínimo de configuração pública do frontend.
- `frontend/app.js` — fluxo de autenticação e alternância de estado da UI.
- `tests/test_supabase_login_flow.py` — verificação estrutural do login.
- `README.md` — instruções curtas de configuração do frontend com Supabase.

## Decisões de design

- Usar `createClient` do Supabase explicitamente para manter aderência clara ao critério da issue.
- Tratar a “IDE” nesta etapa como uma área protegida simples, com mensagem de acesso liberado, sem antecipar editor real.
- Reusar as variáveis públicas do auth foundation (`SUPABASE_URL`, `SUPABASE_ANON_KEY`) e não expor `SUPABASE_JWT_SECRET` no frontend.
- Preferir testes estruturais/contratuais com stdlib para manter a branch reproduzível no estado atual do repositório.

## Verificação

O resultado será considerado pronto quando a branch tiver:

- tela de login com email e senha;
- uso explícito do cliente Supabase para `signInWithPassword`;
- área protegida da IDE exibida após sessão;
- documentação mínima das variáveis públicas do frontend;
- testes automatizados cobrindo esses contratos.
