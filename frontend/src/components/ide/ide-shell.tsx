import { useState, useRef } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import type { ImperativePanelHandle } from "react-resizable-panels";
import { MonacoEditorPane } from "./monaco-editor-pane";
import type { MonacoEditorPaneHandle } from "./monaco-editor-pane";
import { NasmPane } from "./nasm-pane";
import { TerminalPane } from "./terminal-pane";
import type { TerminalPaneHandle } from "./terminal-pane";
import { Toolbar } from "./toolbar";
import type { IdeStatus } from "./toolbar";
import { compileCode } from "../../lib/compile-api";


export function IdeShell() {
  const [status, setStatus] = useState<IdeStatus>("idle");
  const [nasmContent, setNasmContent] = useState("");
  const nasmPanelRef = useRef<ImperativePanelHandle>(null);
  const editorRef = useRef<MonacoEditorPaneHandle>(null);
  const terminalRef = useRef<TerminalPaneHandle>(null);

  function handleDoubleClick() {
    const panel = nasmPanelRef.current;
    if (!panel) return;
    if (panel.isCollapsed()) {
      panel.expand();
    } else {
      panel.collapse();
    }
  }

  async function handleRun() {
    const editor = editorRef.current;
    if (!editor) return;
    const code = editor.getValue();
    editor.clearMarkers();
    terminalRef.current?.clear();
    terminalRef.current?.write("$ simplesc run\n");
    setStatus("compiling");
    try {
      const result = await compileCode(code);
      if (result.ok) {
        setNasmContent(result.nasm);
        terminalRef.current?.write("Compilação concluída com sucesso.\n");
        setStatus("idle");
      } else {
        editor.setMarkers([result.error]);
        setNasmContent(`; Erro de compilação:\n; ${result.error.message}`);
        terminalRef.current?.write(`Erro de compilação: ${result.error.message}\n`);
        setStatus("compile_error");
      }
    } catch (error) {
      setNasmContent("");
      terminalRef.current?.write(`Falha inesperada na compilação: ${String(error)}\n`);
      setStatus("idle");
    }
  }

  return (
    <div id="ide-shell">
      <Toolbar
        status={status}
        onRun={handleRun}
        onStop={() => setStatus("idle")}
      />
      <PanelGroup direction="horizontal" className="ide-panel-group">
        <Panel defaultSize={60} minSize={30}>
          <div className="editor-area">
            <MonacoEditorPane
              ref={editorRef}
              readOnly={status === "compiling"}
            />
          </div>
        </Panel>
        <PanelResizeHandle className="resize-handle" onDoubleClick={handleDoubleClick} />
        <Panel ref={nasmPanelRef} defaultSize={40} minSize={20} collapsible>
          <NasmPane status={status} value={nasmContent} />
        </Panel>
      </PanelGroup>
      <div className="terminal-area">
        <TerminalPane
          ref={terminalRef}
          onData={(data: string) => {
            void data;
            // TODO: forward terminal stdin to websocket transport.
          }}
        />
      </div>
    </div>
  );
}
