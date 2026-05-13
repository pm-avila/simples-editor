# Design: WebSocket `/ws/run` autenticado (Issue #24)

## Problema

O backend atual expõe apenas REST (`/api/compile`) e ainda não existe canal WebSocket autenticado para sessões interativas. A Issue #24 exige handshake com JWT validado no backend e entrada da conexão em uma máquina de estados por sessão.

## Abordagens avaliadas

1. **Flask + Flask-Sock (recomendada)**  
   Reaproveita o backend Flask já existente, adiciona endpoint WS com baixo impacto de arquitetura e permite validar JWT no handshake antes do loop de mensagens.

2. **Migrar backend para ASGI (FastAPI/Quart)**  
   Melhor base para concorrência e async no longo prazo, mas exige refatoração ampla fora do escopo imediato da sprint.

3. **Separar servidor WS em processo dedicado**  
   Isola responsabilidades, porém aumenta complexidade operacional e de deploy agora.

## Recomendação

Adotar **Flask + Flask-Sock** para entregar o requisito com menor risco e máxima aderência ao código atual. A arquitetura mantém fronteiras claras para evoluir depois para engine async sem retrabalho de contrato.

## Arquitetura proposta

```
backend/
├── app.py                       ← registra /ws/run
├── auth.py                      ← valida JWT (reuso)
└── ws/
    ├── protocol.py              ← contrato de mensagens + parser
    ├── state_machine.py         ← estados da conexão (IDLE/COMPILING/EXECUTING)
    └── run_session.py           ← loop WS por conexão
```

## Contrato inicial da Issue #24

- Endpoint WS: `GET /ws/run`
- Autenticação no handshake:
  - `Sec-WebSocket-Protocol: bearer.<jwt>` (preferencial)
  - fallback `?token=<jwt>`
- Se token inválido: rejeita upgrade (401)
- Após conexão aceita:
  - sessão inicia em `IDLE`
  - aceita somente mensagens JSON válidas
  - mensagens fora de estado são descartadas com warning (sem derrubar conexão)

## Fluxo de sessão (escopo da #24)

1. Cliente tenta conectar em `/ws/run` com token.
2. Backend valida JWT (`decode_supabase_jwt` + `extract_user_id`).
3. Se válido, cria contexto de sessão `{user_id, state=IDLE}`.
4. Entra no loop WS com roteamento por estado.
5. Em desconexão, limpa recursos da sessão.

## Erros e robustez

- Payload não-JSON: descarta com resposta `internal_error`/warning conforme contrato.
- Mensagem sem `type`: descarta, mantém conexão.
- Exceção interna inesperada: envia `internal_error` e encerra sessão com cleanup.

## Testes

- `tests/test_ws_run_auth.py`
  - registra endpoint `/ws/run`
  - valida rejeição sem token
  - valida rejeição com token inválido
  - valida aceitação com token válido e inicialização em `IDLE`
- `tests/test_ws_state_machine.py`
  - garante transições válidas e descarte de mensagens inválidas sem crash

## Mapeamento de aceite (Issue #24)

| Critério | Implementação |
|---|---|
| Endpoint `/ws/run` autenticado | `app.py` + `run_session.py` |
| JWT validado no handshake | parser de token + `auth.py` |
| Conexão entra em máquina de estados | `state_machine.py` inicia em `IDLE` |
