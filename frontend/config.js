// Runtime configuration for Supabase
// These values should be set from environment variables during build time
// or injected by the server at runtime
window.__SUPABASE_URL__ = 
  window.__SUPABASE_URL__ || 
  import.meta.env.VITE_SUPABASE_URL || 
  "https://example.supabase.co";
  
window.__SUPABASE_ANON_KEY__ = 
  window.__SUPABASE_ANON_KEY__ || 
  import.meta.env.VITE_SUPABASE_ANON_KEY || 
  "dev-anon-key";

console.log('Supabase URL:', window.__SUPABASE_URL__);
console.log('Supabase Auth configured:', !!window.__SUPABASE_ANON_KEY__);
