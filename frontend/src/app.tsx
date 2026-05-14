import { useEffect, useState } from "react";
import { supabase } from "./lib/supabase";
import { HomePage } from "./components/home/HomePage";
import { IdeShell } from "./components/ide/ide-shell";

export function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [loginError, setLoginError] = useState<string | undefined>();
  const [accessToken, setAccessToken] = useState<string | undefined>();
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setAuthenticated(!!session);
      setAccessToken(session?.access_token);
    });
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setAuthenticated(!!session);
      setAccessToken(session?.access_token ?? undefined);
    });
    return () => subscription.unsubscribe();
  }, []);

  async function handleLogin(email: string, password: string) {
    setLoginError(undefined);
    setIsLoggingIn(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        console.error('Login error:', error);
        setLoginError(error.message);
        setIsLoggingIn(false);
      } else {
        console.log('Login successful, waiting for auth state update...');
        // onAuthStateChange listener will handle setting authenticated
      }
    } catch (err) {
      console.error('Unexpected error:', err);
      setLoginError('Erro ao conectar com o servidor');
      setIsLoggingIn(false);
    }
  }

  async function handleLogout() {
    await supabase.auth.signOut();
    setAuthenticated(false);
    setAccessToken(undefined);
    setLoginError(undefined);
  }

  if (!authenticated) {
    return (
      <HomePage
        onSubmit={handleLogin}
        error={loginError}
        isLoading={isLoggingIn}
      />
    );
  }

  return <IdeShell token={accessToken} onLogout={handleLogout} />;
}
