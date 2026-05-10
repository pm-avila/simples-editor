# simples-editor

## Backend JWT validation

Sprint 1 validates Supabase JWTs in the backend with a shared `verify_jwt` mechanism.

The backend depends on:

- `SUPABASE_JWT_SECRET`

The validator decodes the JWT locally, extracts `user_id` from the `sub` claim, and protects backend handlers without querying the database for each request.
