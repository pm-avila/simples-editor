export type IdeStatus = "idle" | "compiling" | "executing" | "compile_error";

interface ToolbarProps {
  status: IdeStatus;
  onRun: () => void;
  onStop: () => void;
}

export function Toolbar({ status, onRun, onStop }: ToolbarProps) {
  const isRunning = status === "compiling" || status === "executing";
  return (
    <header className="toolbar">
      {isRunning ? (
        <button className="toolbar__stop-btn" onClick={onStop}>
          Stop
        </button>
      ) : (
        <button className="toolbar__run-btn" onClick={onRun}>
          Run
        </button>
      )}
    </header>
  );
}
