# Backend JWT Validation Design

## Problema

A issue #7 pede um mecanismo compartilhado como `@verify_jwt` para validar tokens do Supabase no backend e extrair `user_id` a partir do claim `sub`. A branch `dev` ainda não tem um backend funcional versionado, então a solução precisa ser autocontida, pequena e reutilizável por futuros endpoints REST e conexões WebSocket.

## Escopo aprovado

- Tornar a branch `feat/7` autocontida para a fundação de validação JWT do backend.
- Criar um módulo compartilhado de autenticação com decorator e helpers pequenos.
- Validar JWT do Supabase localmente usando `SUPABASE_JWT_SECRET`.
- Extrair `user_id` a partir de `sub`.
- Cobrir tanto o fluxo de requests quanto o modelo de conexão com helpers reaproveitáveis.
- Manter a solução testável sem depender de um app Flask completo.

## Fora de escopo

- Criar endpoints finais do backend.
- Implementar `/api/health`; isso fica para a issue #8.
- Integrar WebSocket real; nesta issue basta que o contrato seja reutilizável para conexões.
- Introduzir banco de dados ou consulta ao Supabase para validar requests.

## Abordagens consideradas

### 1. Módulo isolado de auth com decorator e helpers compartilhados (**escolhida**)

Pró: resolve o critério central com baixo acoplamento e prepara REST/WebSocket.  
Contra: ainda não exercita um servidor real.

### 2. Integrar a validação já dentro de endpoints Flask concretos

Pró: aproxima da integração final.  
Contra: mistura a issue #7 com a #8 e aumenta o escopo cedo demais.

### 3. Validar token manualmente em cada handler

Pró: implementação curta.  
Contra: contradiz o objetivo explícito de mecanismo compartilhado.

## Abordagem escolhida

A solução será um módulo `backend/auth.py` com quatro peças:

1. `AuthError` para falhas explícitas de autenticação;
2. `decode_supabase_jwt(token, jwt_secret)` para validar assinatura e claims mínimas;
3. `extract_user_id(claims)` para obter o `sub` de forma centralizada;
4. `verify_jwt(handler)` como decorator compartilhado que resolve o token, valida o JWT e injeta `user_id` no contexto do handler.

## Estrutura proposta

- `backend/__init__.py` — marca o backend como pacote.
- `backend/auth.py` — módulo compartilhado de autenticação.
- `backend/requirements.txt` — dependência explícita de `PyJWT`.
- `tests/test_backend_auth.py` — suíte de regressão para o contrato de autenticação.
- `README.md` — nota curta sobre validação local de JWT no backend.

## Decisões de design

- Tratar o backend como validador offline do JWT emitido pelo Supabase, sem consulta ao banco.
- Fazer o decorator operar sobre um request-like object simples para evitar dependência prematura em Flask real.
- Separar parsing/decoding de token e extração de `user_id` para facilitar reaproveitamento em requests e conexões.
- Falhar de forma explícita quando o token estiver ausente, inválido ou sem `sub`.

## Verificação

O resultado será considerado pronto quando a branch tiver:

- módulo compartilhado de autenticação com `verify_jwt`;
- extração explícita de `user_id` a partir de `sub`;
- contrato testado para ausência de token, token inválido e token válido;
- documentação curta deixando claro que o backend valida JWT do Supabase localmente com `SUPABASE_JWT_SECRET`.
