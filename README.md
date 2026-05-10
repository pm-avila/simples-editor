# simples-editor

## Supabase auth foundation

Sprint 1 uses Supabase as the identity provider for v1. The repository expects the local environment to provide:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`

Copy `.env.example` to `.env` and replace the placeholder values with the project credentials for your Supabase environment.

The authentication model is based on Supabase Auth and its native `auth.users` table. The backend will validate JWT locally with the shared secret, without querying the database for each request.
