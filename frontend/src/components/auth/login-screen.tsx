import { useState } from "react";

interface LoginScreenProps {
  onSubmit: (email: string, password: string) => void;
  error?: string;
}

export function LoginScreen({ onSubmit, error }: LoginScreenProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <div id="login-screen">
      <h1>Simples Editor</h1>
      <form
        id="login-form"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit(email, password);
        }}
      >
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <button type="submit">Sign In</button>
      </form>
    </div>
  );
}
