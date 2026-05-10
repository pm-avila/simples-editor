# simples-editor

## Supabase login

Sprint 1 uses Supabase email/password authentication in the frontend before releasing access to the IDE shell.

The frontend login flow depends on:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

Configure those values before loading the login page by defining:

- `window.__SUPABASE_URL__`
- `window.__SUPABASE_ANON_KEY__`

Example:

```html
<script>
  window.__SUPABASE_URL__ = "https://your-project.supabase.co";
  window.__SUPABASE_ANON_KEY__ = "your-anon-key";
</script>
```

The form sends email/password credentials to Supabase and reveals the protected “IDE access granted” shell after a valid session exists.
