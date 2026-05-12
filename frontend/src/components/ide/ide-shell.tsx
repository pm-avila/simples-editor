import { MonacoEditorPane } from "./monaco-editor-pane";
import { NasmPane } from "./nasm-pane";
import { TerminalPane } from "./terminal-pane";


export function IdeShell() {
  return (
    <div id="ide-shell">
      <div className="editor-area">
        <MonacoEditorPane />
      </div>
      <NasmPane />
      <TerminalPane />
    </div>
  );
}
