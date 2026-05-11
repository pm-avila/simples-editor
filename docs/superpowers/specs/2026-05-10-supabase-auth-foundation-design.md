# Supabase Auth Foundation Design

## Problema

A issue #5 pede a fundação de autenticação do Supabase para o v1, mas a branch `dev` ainda não contém a estrutura local introduzida nas issues #3 e #4. Além disso, criar um projeto cloud real do Supabase exigiria credenciais externas e deixaria a automação da Sprint 1 dependente de estado fora do repositório.

## Escopo aprovado

- Tornar a branch `feat/5` autocontida para a fundação de auth do Supabase.
- Versionar o contrato mínimo de ambiente para auth: URL do projeto, chave pública e JWT secret.
- Versionar uma configuração declarativa do Supabase para deixar explícito que o auth do v1 usa `auth.users` como base nativa.
- Adicionar uma fundação mínima de backend para carregar essas variáveis e explicitar que a validação do JWT será local, sem consulta ao banco.
- Cobrir esse contrato com testes reprodutíveis sem depender de credenciais reais.

## Fora de escopo

- Criar um projeto cloud real no Supabase durante esta issue.
- Implementar tela de login no frontend.
- Validar JWT em endpoints protegidos; isso fica para a issue #7.
- Expor endpoint de health check; isso fica para a issue #8.

## Abordagens consideradas

### 1. Provisionar um projeto real do Supabase agora

Pró: atenderia literalmente o critério "existe um projeto".  
Contra: exige credenciais e estado externo, reduz reprodutibilidade e fragiliza a automação.

### 2. Documentação e `.env.example` apenas

Pró: simples e barata.  
Contra: deixa a fundação frouxa demais e não cria um ponto técnico reutilizável para o backend.

### 3. Fundação declarativa e versionada no repositório (**escolhida**)

Pró: mantém a issue automatizável, cria contrato testável e prepara diretamente as issues #7 e #8.  
Contra: não materializa um tenant cloud real, então o resultado precisa deixar claro que a branch expressa a configuração esperada do projeto Supabase do v1.

## Abordagem escolhida

A solução será uma fundação declarativa de auth do Supabase dentro da própria branch `feat/5`. Em vez de depender de um projeto externo criado manualmente, a branch vai expressar o contrato mínimo necessário para o v1 através de:

1. um `.env.example` com `SUPABASE_URL`, `SUPABASE_ANON_KEY` e `SUPABASE_JWT_SECRET`;
2. um arquivo versionado de configuração do Supabase para deixar explícito que a autenticação é a nativa da plataforma, baseada em `auth.users`;
3. um módulo mínimo de backend para carregar e expor essa configuração;
4. documentação curta explicando que o backend validará JWT localmente, sem consultar o banco.

## Estrutura proposta

- `supabase/config.toml` — contrato declarativo do projeto local de auth.
- `.env.example` — variáveis obrigatórias de integração.
- `backend/requirements.txt` — dependências mínimas do backend.
- `backend/auth_config.py` — leitura/normalização das variáveis de auth.
- `backend/README.md` ou atualização do `README.md` — explicação curta do modelo de autenticação do v1.
- `tests/test_supabase_auth_foundation.py` — verificação estrutural do contrato.

## Decisões de design

- Reusar os nomes de variáveis já previstos nas issues de compose para evitar churn desnecessário depois.
- Modelar a configuração do backend em um arquivo pequeno e isolado, sem antecipar ainda decorator, rotas ou lógica de autorização.
- Tratar o Supabase como provedor de identidade e emissão de JWT; o backend apenas consome `SUPABASE_JWT_SECRET` para futura validação offline.
- Deixar explícito em código e documentação que o backend não consulta o banco para autenticar requests no v1.

## Verificação

O resultado será considerado pronto quando a branch tiver:

- contrato versionado para `SUPABASE_URL`, `SUPABASE_ANON_KEY` e `SUPABASE_JWT_SECRET`;
- configuração declarativa do Supabase presente no repositório;
- módulo de backend que centraliza a leitura dessa configuração;
- documentação deixando claro o modelo "JWT validado localmente, sem consulta ao banco";
- testes automatizados cobrindo esses pontos sem depender de credenciais reais.
