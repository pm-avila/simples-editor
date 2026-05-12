type IdeStatus = "idle" | "compiling";

interface NasmPaneProps {
  status: IdeStatus;
}

export function NasmPane({ status = "idle" }: NasmPaneProps) {
  return (
    <aside className="nasm-pane">
      <header className="nasm-pane__header">NASM x32</header>
      <div className="nasm-pane__body">
        {status === "compiling" && (
          <p className="nasm-pane__mock-msg">compilando… (mock)</p>
        )}
      </div>
    </aside>
  );
}
