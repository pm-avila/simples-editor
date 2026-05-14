import { useState } from "react";
import "./landing-redesign.css";

interface LoginScreenProps {
  onSubmit: (email: string, password: string) => void;
  error?: string;
}

export function LoginScreen({ onSubmit, error }: LoginScreenProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <div className="landing-container">
      <pre className="landing-logo">{`
  ███████╗██╗███╗   ███╗██████╗ ██╗     ███████╗███████╗
  ██╔════╝██║████╗ ████║██╔══██╗██║     ██╔════╝██╔════╝
  ███████╗██║██╔████╔██║██████╔╝██║     █████╗  █████╗
  ╚════██║██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ██╔══╝
  ███████║██║██║ ╚═╝ ██║██║     ███████╗███████╗███████╗
  ╚══════╝╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚══════╝
      `}</pre>
      <h1 className="landing-title">VISUAL SIMPLES</h1>
      <form className="landing-form" onSubmit={(e) => {
        e.preventDefault();
        onSubmit(email, password);
      }}>
        <input
          type="email"
          placeholder="user@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p role="alert" className="landing-error">{error}</p>}
        <button type="submit" className="landing-button">LOGIN</button>
      </form>
      <div className="landing-footer">
        Powered by Simples • Compiled Code Editor
      </div>
    </div>
  );
}
