import { useEffect, useState } from "react";
import { supabase } from "./lib/supabase";
import { LoginScreen } from "./components/auth/login-screen";
import { IdeShell } from "./components/ide/ide-shell";

export function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [loginError, setLoginError] = useState<string | undefined>();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setAuthenticated(!!session);
    });
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setAuthenticated(!!session);
    });
    return () => subscription.unsubscribe();
  }, []);

  async function handleLogin(email: string, password: string) {
    setLoginError(undefined);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) setLoginError(error.message);
  }

  if (!authenticated) {
    return <LoginScreen onSubmit={handleLogin} error={loginError} />;
  }

  return <IdeShell />;
}
