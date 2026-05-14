export type IdeStatus = "idle" | "compiling" | "executing" | "compile_error";

interface ToolbarProps {
  status: IdeStatus;
  onRun: () => void;
  onStop: () => void;
}

export function Toolbar({ status, onRun, onStop }: ToolbarProps) {
  const isRunning = status === "compiling" || status === "executing";
  return (
    <header className="toolbar-dos">
      <div className="toolbar-section">
        <button className="toolbar-button" onClick={isRunning ? onStop : onRun} disabled={false}>
          {isRunning ? "Stop" : "Run"}
        </button>
        {status === "compiling" && <span className="toolbar-status">Compiling...</span>}
        {status === "executing" && <span className="toolbar-status">Running...</span>}
        {status === "compile_error" && <span className="toolbar-status-error">Compile Error</span>}
      </div>
    </header>
  );
}
