import Editor from "@monaco-editor/react";
import { SIMPLES_THEME_ID } from "./simples-theme";
import type { IdeStatus } from "./toolbar";

interface NasmPaneProps {
  status?: IdeStatus;
  value?: string;
}

const PLACEHOLDER = "; Execute o programa para ver o assembly gerado.";
const COMPILING   = "; Compilando…";

export function NasmPane({ status = "idle", value = "" }: NasmPaneProps) {
  let editorValue: string;
  if (status === "compiling") {
    editorValue = COMPILING;
  } else if (value) {
    editorValue = value;
  } else {
    editorValue = PLACEHOLDER;
  }

  return (
    <aside className="nasm-pane">
      <header className="nasm-pane__header">NASM x32</header>
      <div className="nasm-pane__body">
        <Editor
          height="100%"
          language="asm"
          theme={SIMPLES_THEME_ID}
          value={editorValue}
          options={{ readOnly: true, minimap: { enabled: false } }}
        />
      </div>
    </aside>
  );
}
