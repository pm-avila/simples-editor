import { useState } from "react";
import "./landing-redesign.css";

interface LoginScreenProps {
  onSubmit: (email: string, password: string) => void;
  error?: string;
}

export function LoginScreen({ onSubmit, error }: LoginScreenProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      onSubmit(email, password);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="landing-container">
      <header className="landing-header">
        <div className="landing-logo-text">
          <span className="landing-logo-icon"></span>
          SIMPLES
        </div>
      </header>

      <main className="landing-main">
        <div className="landing-hero">
          <h1 className="landing-title">Simples Editor</h1>
          <p className="landing-subtitle">Compilador web para a linguagem SIMPLES</p>
        </div>

        <div className="landing-card">
          <form className="landing-form" onSubmit={handleSubmit}>
            {error && (
              <div role="alert" className="landing-error-message">
                {error}
              </div>
            )}

            <div className="landing-form-group">
              <label htmlFor="email" className="landing-label">Email</label>
              <input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="landing-input"
              />
            </div>

            <div className="landing-form-group">
              <label htmlFor="password" className="landing-label">Senha</label>
              <div className="landing-password-wrapper">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  className="landing-input"
                />
                <button
                  type="button"
                  className="landing-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                >
                  {showPassword ? "Ocultar" : "Mostrar"}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="landing-button"
            >
              {isLoading ? (
                <>
                  <span className="landing-loading"></span>
                  <span className="landing-loading"></span>
                  <span className="landing-loading"></span>
                </>
              ) : (
                "Entrar na IDE"
              )}
            </button>

            <div className="landing-form-footer">
              Primeira vez? <a href="#signup">Crie uma conta</a>
            </div>
          </form>

          <div className="landing-features">
            <div className="landing-feature">
              <div className="landing-feature-icon">⚡</div>
              <div className="landing-feature-label">Compile</div>
            </div>
            <div className="landing-feature">
              <div className="landing-feature-icon">🔍</div>
              <div className="landing-feature-label">Visualize</div>
            </div>
            <div className="landing-feature">
              <div className="landing-feature-icon">▶️</div>
              <div className="landing-feature-label">Execute</div>
            </div>
          </div>
        </div>
      </main>

      <footer className="landing-footer">
        <p>
          Simples Editor © 2026 · 
          <a href="#privacy">Privacidade</a> · 
          <a href="#terms">Termos</a>
        </p>
      </footer>
    </div>
  );
}
