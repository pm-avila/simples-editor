import { useCallback, useRef, useState } from "react";
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
import { createRunSessionClient } from "../../lib/run-session-client";
import type { RunSessionClient } from "../../lib/run-session-client";


export function IdeShell({ token }: { token?: string }) {
  const [status, setStatus] = useState<IdeStatus>("idle");
  const [nasmContent, setNasmContent] = useState("");
  const nasmPanelRef = useRef<ImperativePanelHandle>(null);
  const editorRef = useRef<MonacoEditorPaneHandle>(null);
  const terminalRef = useRef<TerminalPaneHandle>(null);
  const runSessionRef = useRef<RunSessionClient | null>(null);
  const handleRunSessionEvent = useCallback((payload: Record<string, unknown>) => {
    if (payload.type === "exec_started") {
      setStatus("executing");
      return;
    }

    if (payload.type === "exit" || payload.type === "timeout") {
      setStatus("idle");
      return;
    }

    if (payload.type === "runtime_error") {
      setStatus("idle");
      return;
    }

    if (payload.type === "rate_limited") {
      terminalRef.current?.write("Limite de uso atingido. Tente novamente mais tarde.\r\n");
      setStatus("idle");
    }
  }, []);

  const handleRunSessionClose = useCallback(() => {
    setStatus((prev) => (prev === "executing" ? "idle" : prev));
  }, []);
  const handleTerminalData = useCallback((data: string) => {
    runSessionRef.current?.sendStdin(data);
  }, []);

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
    terminalRef.current?.write("$ simplesc run\r\n");
    setStatus("compiling");
    try {
      const result = await compileCode(code);
      if (result.ok) {
        setNasmContent(result.nasm);
        terminalRef.current?.write("Compilação concluída com sucesso.\r\n");
        if (!runSessionRef.current) {
          runSessionRef.current = createRunSessionClient({
            onStdout: (data) => terminalRef.current?.write(data),
            onEvent: handleRunSessionEvent,
            onClose: handleRunSessionClose,
            token,
          });
        }
        runSessionRef.current?.start(code);
        setStatus("executing");
      } else {
        editor.setMarkers([result.error]);
        setNasmContent(`; Erro de compilação:\n; ${result.error.message}`);
        terminalRef.current?.write(`Erro de compilação: ${result.error.message}\r\n`);
        setStatus("compile_error");
      }
    } catch (error) {
      setNasmContent("");
      terminalRef.current?.write(`Falha inesperada na compilação: ${String(error)}\r\n`);
      setStatus("idle");
    }
  }

  return (
    <div id="ide-shell">
      <Toolbar
          status={status}
          onRun={handleRun}
          onStop={() => {
            runSessionRef.current?.stop();
          }}
        />
      <PanelGroup direction="horizontal" className="ide-panel-group">
        <Panel defaultSize={60} minSize={30}>
          <div className="editor-area">
            <MonacoEditorPane
              ref={editorRef}
              readOnly={status === "compiling" || status === "executing"}
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
          onData={handleTerminalData}
        />
      </div>
    </div>
  );
}
