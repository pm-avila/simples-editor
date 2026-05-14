import { useState } from "react";
import "./landing-redesign.css";
import "./login-retro-nerd.css";

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
    <div className="landing-container retro-nerd">
      <header className="landing-header retro-nerd">
        <div className="landing-logo-text">
          <span className="landing-logo-icon"></span>
          SIMPLES
        </div>
      </header>

      <main className="landing-main">
        <div className="landing-hero">
          <h1 className="landing-title retro-nerd">
███████╗██╗███╗   ███╗██████╗ ██╗     ███████╗███████╗
██╔════╝██║████╗ ████║██╔══██╗██║     ██╔════╝██╔════╝
███████╗██║██╔████╔██║██████╔╝██║     █████╗  ███████╗
╚════██║██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ╚════██║
███████║██║██║ ╚═╝ ██║██║     ███████╗███████╗███████║
╚══════╝╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚══════╝
          </h1>
          <p className="landing-subtitle retro-nerd">[COMPILER ENVIRONMENT v1.0]</p>
        </div>

        <div className="landing-card retro-nerd">
          <form className="landing-form" onSubmit={handleSubmit}>
            {error && (
              <div role="alert" className="landing-error-message retro-nerd">
                {error}
              </div>
            )}

            <div className="landing-form-group">
              <label htmlFor="email" className="landing-label retro-nerd">Email</label>
              <input
                id="email"
                type="email"
                placeholder="usuario@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="landing-input retro-nerd"
              />
            </div>

            <div className="landing-form-group">
              <label htmlFor="password" className="landing-label retro-nerd">Senha</label>
              <div className="landing-password-wrapper">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  className="landing-input retro-nerd"
                />
                <button
                  type="button"
                  className="landing-password-toggle retro-nerd"
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
              className="landing-button retro-nerd"
            >
              {isLoading ? (
                <>
                  <span className="landing-loading"></span>
                  <span className="landing-loading"></span>
                  <span className="landing-loading"></span>
                </>
              ) : (
                "Entrar"
              )}
            </button>

            <div className="landing-form-footer retro-nerd">
              Primeira vez? <a href="#signup">Crie uma conta</a>
            </div>
          </form>

          <div className="landing-features retro-nerd">
            <div className="landing-feature retro-nerd">
              <div className="landing-feature-icon retro-nerd">⚡</div>
              <div className="landing-feature-label retro-nerd">Compile</div>
            </div>
            <div className="landing-feature retro-nerd">
              <div className="landing-feature-icon retro-nerd">🔍</div>
              <div className="landing-feature-label retro-nerd">Visualize</div>
            </div>
            <div className="landing-feature retro-nerd">
              <div className="landing-feature-icon retro-nerd">▶️</div>
              <div className="landing-feature-label retro-nerd">Execute</div>
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
