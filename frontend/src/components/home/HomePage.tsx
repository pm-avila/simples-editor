import React from 'react';
import './home-page.css';

interface HomePageProps {
  onLoginClick?: () => void;
  onSignupClick?: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onLoginClick, onSignupClick }) => {
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const email = (e.target as HTMLFormElement).email?.value;
    console.log('Iniciando login com:', email);
    onLoginClick?.();
  };

  const handleGitHubLogin = () => {
    console.log('Login com GitHub');
    onLoginClick?.();
  };

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand-small">[ SIMPLES v1.0 ]</div>
        <nav className="menu" aria-label="Menu principal">
          <a href="#home">[ Home ]</a>
          <a href="#docs">[ Docs ]</a>
          <a href="#exemplos">[ Exemplos ]</a>
          <a href="https://github.com/pm-avila/simples-compiler" target="_blank" rel="noreferrer">[ GitHub ]</a>
          <a href="#sobre">[ Sobre ]</a>
        </nav>
      </header>

      <main className="main" id="home">
        <section className="content">
          <div className="hero-grid">
            <div>
              <pre className="ascii-logo" aria-label="SIMPLES">{`  _____ _____ __  __ _____  _      ______  _____
 / ____|_   _|  \\/  |  __ \\| |    |  ____|/ ____|
| (___   | | | \\  / | |__) | |    | |__  | (___
 \\___ \\  | | | |\\/| |  ___/| |    |  __|  \\___ \\
 ____) |_| |_| |  | | |    | |____| |____ ____) |
|_____/|_____|_|  |_|_|    |______|______|_____/`}</pre>
              <h1 className="tagline">A linguagem simples. O futuro é simples.</h1>
              <p className="subtitle">Editor de código online para a linguagem SIMPLES</p>
            </div>

            <pre className="computer-art" aria-hidden="true">{`        ______________________
       / ==================== /|
      / ==================== / |
     /______________________/  |
     |  __________________  |  |
     | |                  | |  |
     | |     SIMPLES > _   | |  |
     | |__________________| | /
     |______________________|/
        ||  ||        ||  ||
        ||__||________||__||
       /____________________\\
      / [] [] [] [] [] [] [] \\
     /________________________\\`}</pre>
          </div>

          <section className="terminal-card blue" id="sobre">
            <h2 className="terminal-title">$ sobre simples</h2>
            <p>
              SIMPLES é uma linguagem educacional, minimalista e poderosa. Criada para ensinar conceitos de compiladores, algoritmos e estruturas de dados de forma prática e direta.
            </p>
            <ul>
              <li>Sintaxe clara e objetiva</li>
              <li>Tipagem estática com suporte a arrays e estruturas</li>
              <li>Compilada para código C de alto desempenho</li>
              <li>Ideal para fins didáticos e acadêmicos</li>
              <li>Projeto open-source sob GPL-3.0</li>
            </ul>
            <p className="quote">
              "Simplificar para ensinar. Essa é a ideia."
              <span>-- Paulo Avila</span>
            </p>
          </section>

          <section className="terminal-card yellow" id="exemplos">
            <h2 className="terminal-title">$ exemplo_hello_world.simples</h2>
            <div className="code-row">
              <div className="code-block">
                <div>
                  <span className="kw">programa</span> <span className="id">OlaMundo</span>;
                </div>
                <div>
                  <span className="kw">inicio</span>
                </div>
                <div>
                  &nbsp;&nbsp;<span className="kw">escreva</span>
                  (<span className="str">"Olá, Mundo SIMPLES!"</span>);{' '}
                  <span className="comment">// Primeira linha</span>
                </div>
                <div>
                  <span className="kw">fim.</span>
                </div>
                <br />
                <div className="run">{`>>> compilando...`}</div>
                <div className="run">{`>>> executando...`}</div>
                <div className="ok">✓ Olá, Mundo SIMPLES!</div>
              </div>

              <pre className="nerd-art" aria-hidden="true">{`        .-"""-. 
       /  .-.  \\
      |  /   \\  |
      | | o o | |
      | |  ^  | |
      | | '-' | |
       \\ \\___/ /
        '.___.'
       /|\\___/|\\
      /_|     |_\\
        |  |  |
       _|__|__|_
      /___/ \\___\\`}</pre>
            </div>
          </section>
        </section>

        <aside className="login-panel" aria-label="Login e acesso">
          <div className="panel-title">≡ Acesse sua conta</div>
          <pre className="lock-art" aria-hidden="true">{`       _______
      / _____ \\
     / /     \\ \\
     | |     | |
   __| |_____| |__
  |  ___________  |
  | |     ◉     | |
  | |    / \\    | |
  | |___|   |___| |
  |_______________|`}</pre>
          <p>Entre com suas credenciais para acessar o editor.</p>

          <form id="login-form" onSubmit={handleLogin}>
            <label htmlFor="email">E-mail</label>
            <input
              id="email"
              name="email"
              type="email"
              placeholder="seu@email.com"
              autoComplete="email"
              required
            />

            <label htmlFor="password">Senha</label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="••••••••••"
              autoComplete="current-password"
              required
            />

            <a className="forgot" href="#recuperar">
              [ Esqueceu sua senha? ]
            </a>

            <button className="btn btn-primary" type="submit">
              [ Entrar ]
            </button>
          </form>

          <div className="signup">
            Ainda não tem conta?{' '}
            <a href="#cadastro" onClick={onSignupClick}>
              [ Cadastre-se agora ]
            </a>
          </div>
          <div className="divider">-- ou --</div>

          <button
            className="btn btn-github"
            type="button"
            onClick={handleGitHubLogin}
          >
            <span aria-hidden="true">{`{~}`}</span>
            Entrar com GitHub
          </button>

          <div className="supabase">
            <div className="bolt">ϟ</div>
            <div>
              <strong>Autenticação via Supabase</strong>
              <span>Seguro. Rápido. Open Source.</span>
            </div>
          </div>
        </aside>
      </main>

      <footer className="footer">
        <span>SIMPLES Online Editor v1.0</span>
        <span>Feito com &lt;3 por Paulo Avila</span>
        <span>GPL-3.0 License</span>
      </footer>
    </div>
  );
};
