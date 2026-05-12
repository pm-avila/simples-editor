type IdeStatus = "idle" | "compiling";

interface ToolbarProps {
  status: IdeStatus;
  onRun: () => void;
  onStop: () => void;
}

export function Toolbar({ status, onRun, onStop }: ToolbarProps) {
  return (
    <header className="toolbar">
      {status === "idle" ? (
        <button className="toolbar__run-btn" onClick={onRun}>
          Run
        </button>
      ) : (
        <button className="toolbar__stop-btn" onClick={onStop}>
          Stop
        </button>
      )}
    </header>
  );
}
