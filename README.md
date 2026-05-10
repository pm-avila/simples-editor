# simples-editor

## Desenvolvimento local com Docker Compose

O fluxo local real entra sempre pelo **nginx**. Ele é o único ponto de entrada exposto no host:

- `http://localhost/` responde o frontend
- `http://localhost/api/` encaminha as requisições para o backend

### Como subir o ambiente

1. Copie `.env.example` para `.env`
2. Execute `docker compose up --build`
3. Acesse `http://localhost`

Exemplo:

```bash
cp .env.example .env
docker compose up --build
```
