import { useEffect, useState } from "react";
import { supabase } from "./lib/supabase";
import { LoginScreen } from "./components/auth/login-screen";
import { HomePage } from "./components/home/HomePage";
import { IdeShell } from "./components/ide/ide-shell";

export function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [showHome, setShowHome] = useState(true);
  const [loginError, setLoginError] = useState<string | undefined>();
  const [accessToken, setAccessToken] = useState<string | undefined>();

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
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) setLoginError(error.message);
  }

  async function handleLogout() {
    await supabase.auth.signOut();
    setAuthenticated(false);
    setAccessToken(undefined);
    setShowHome(true);
  }

  if (!authenticated) {
    if (showHome) {
      return (
        <HomePage
          onLoginClick={() => setShowHome(false)}
          onSignupClick={() => setShowHome(false)}
        />
      );
    }
    return <LoginScreen onSubmit={handleLogin} error={loginError} />;
  }

  return <IdeShell token={accessToken} onLogout={handleLogout} />;
}
