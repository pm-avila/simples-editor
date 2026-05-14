import { useState } from "react";

export type IdeStatus = "idle" | "compiling" | "executing" | "compile_error";

export interface Example {
  name: string;
  code: string;
}

interface ToolbarProps {
  status: IdeStatus;
  onRun: () => void;
  onStop: () => void;
  onLogout?: () => void;
  onExampleSelect?: (example: Example) => void;
  examples?: Example[];
}

export function Toolbar({ status, onRun, onStop, onLogout, onExampleSelect, examples = [] }: ToolbarProps) {
  const isRunning = status === "compiling" || status === "executing";
  const [showExamples, setShowExamples] = useState(false);

  const handleSelectExample = (example: Example) => {
    onExampleSelect?.(example);
    setShowExamples(false);
  };

  return (
    <header className="toolbar-dos">
      <div className="toolbar-section">
        <button className="toolbar-button" onClick={isRunning ? onStop : onRun} disabled={false}>
          {isRunning ? "Stop" : "Run"}
        </button>
        {status === "compiling" && <span className="toolbar-status">Compiling...</span>}
        {status === "executing" && <span className="toolbar-status">Running...</span>}
        {status === "compile_error" && <span className="toolbar-status-error">Compile Error</span>}
        
        {examples.length > 0 && (
          <div className="toolbar-examples-dropdown">
            <button className="toolbar-button" onClick={() => setShowExamples(!showExamples)}>
              Exemplos ▼
            </button>
            {showExamples && (
              <div className="examples-dropdown-menu">
                {examples.map((example, idx) => (
                  <button
                    key={idx}
                    className="example-item"
                    onClick={() => handleSelectExample(example)}
                  >
                    {example.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      {onLogout && (
        <div className="toolbar-section" style={{ marginLeft: "auto" }}>
          <button className="toolbar-button" onClick={onLogout}>
            Sair
          </button>
        </div>
      )}
    </header>
  );
}
