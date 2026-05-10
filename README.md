# simples-editor

## Supabase login

Sprint 1 uses Supabase email/password authentication in the frontend before releasing access to the IDE shell.

The frontend login flow depends on:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

Configure those values before loading the login page. The form sends email/password credentials to Supabase and reveals the protected “IDE access granted” shell after a valid session exists.
