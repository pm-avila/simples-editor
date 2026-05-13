import { useRef } from "react";
import Editor from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { SIMPLES_THEME_ID, defineSimplesDarkTheme } from "./simples-theme";
import { registerNasmLanguage, NASM_LANGUAGE_ID } from "./nasm-language";
import type { IdeStatus } from "./toolbar";

interface NasmPaneProps {
  status?: IdeStatus;
  value?: string;
}

const PLACEHOLDER = "; Execute o programa para ver o assembly gerado.";
const COMPILING   = "; compilando...";

export function NasmPane({ status = "idle", value = "" }: NasmPaneProps) {
  const registeredRef = useRef(false);

  let editorValue: string;
  if (status === "compiling") {
    editorValue = COMPILING;
  } else if (value) {
    editorValue = value;
  } else {
    editorValue = PLACEHOLDER;
  }

  function beforeMount(monaco: typeof Monaco) {
    if (!registeredRef.current) {
      defineSimplesDarkTheme(monaco);
      registerNasmLanguage(monaco);
      registeredRef.current = true;
    }
  }

  return (
    <aside className="nasm-pane">
      <header className="nasm-pane__header">NASM x32</header>
      <div className="nasm-pane__body">
        <Editor
          height="100%"
          language={NASM_LANGUAGE_ID}
          theme={SIMPLES_THEME_ID}
          beforeMount={beforeMount}
          value={editorValue}
          options={{ readOnly: true, minimap: { enabled: false } }}
        />
      </div>
    </aside>
  );
}
