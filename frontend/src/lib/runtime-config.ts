declare global {
  interface Window {
    __SUPABASE_URL__?: string;
    __SUPABASE_ANON_KEY__?: string;
  }
}

export const runtimeConfig = {
  supabaseUrl: window.__SUPABASE_URL__ ?? "",
  supabaseAnonKey: window.__SUPABASE_ANON_KEY__ ?? "",
};
