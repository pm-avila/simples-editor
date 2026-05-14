import { useCallback, useRef, useState, useMemo } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import type { ImperativePanelHandle } from "react-resizable-panels";
import { MonacoEditorPane } from "./monaco-editor-pane";
import type { MonacoEditorPaneHandle } from "./monaco-editor-pane";
import { NasmPane } from "./nasm-pane";
import { TerminalPane } from "./terminal-pane";
import type { TerminalPaneHandle } from "./terminal-pane";
import { Toolbar } from "./toolbar";
import type { IdeStatus, Example } from "./toolbar";
import { compileCode } from "../../lib/compile-api";
import { createRunSessionClient } from "../../lib/run-session-client";
import type { RunSessionClient } from "../../lib/run-session-client";

const SIMPLES_EXAMPLES: Example[] = [
  {
    name: "Olá Mundo",
    code: `programa demo
inteiro x;
inicio
x <- (2 + 3) * (4 - 1);
escreva x;
escreval x;
fim`,
  },
  {
    name: "Entrada/Saída",
    code: `programa demo
inteiro x;
inicio
  leia x;
  escreval x;
fim`,
  },
  {
    name: "Fibonacci",
    code: `procedimento inteiro fibonacci(inteiro n)
inicio
  inteiro i, a, b, tmp;
  a <- 0;
  b <- 1;
  se n = 0 entao
    retorna 0;
  senao
    se n = 1 entao
      retorna 1;
    senao
      para i de 2 ate n passo 1 faca
        tmp <- a + b;
        a <- b;
        b <- tmp;
      fimpara
      retorna b;
    fimse
  fimse
fim

programa demo
inteiro n, i;
inicio
  escreva "digite o numero: ";
  leia n;
  se n > 46 entao
    escreval "numero muito grande";
  senao
    escreva "fibonacci ate ";
    escreva n;
    escreval ":";
    para i de 0 ate n passo 1 faca
      escreva fibonacci(i);
      se i < n entao
        escreva " ";
      fimse
    fimpara
    escreval "";
  fimse
fim`,
  },
  {
    name: "Fatorial",
    code: `procedimento inteiro fatorial(inteiro n)
inicio
  inteiro i, resultado;
  resultado <- 1;
  para i de 2 ate n passo 1 faca
    resultado <- resultado * i;
  fimpara
  retorna resultado;
fim

programa demo
inteiro x;
inicio
  escreva "digite o numero: ";
  leia x;
  escreva "fatorial de ";
  escreva x;
  escreva " = ";
  escreval fatorial(x);
fim`,
  },
  {
    name: "Matriz 2D",
    code: `programa demo
inteiro m[3][4];
inteiro i, j;
inicio
  para i de 0 ate 2 passo 1 faca
    para j de 0 ate 3 passo 1 faca
      m[i][j] <- i * 10 + j;
    fimpara
  fimpara

  para i de 0 ate 2 passo 1 faca
    para j de 0 ate 3 passo 1 faca
      escreva m[i][j];
      se j < 3 entao
        escreva " ";
      fimse
    fimpara
    escreval "";
  fimpara
fim`,
  },
];

export function IdeShell({ token, onLogout }: { token?: string; onLogout?: () => void }) {
  const [status, setStatus] = useState<IdeStatus>("idle");
  const [nasmContent, setNasmContent] = useState("");
  const nasmPanelRef = useRef<ImperativePanelHandle>(null);
  const editorRef = useRef<MonacoEditorPaneHandle>(null);
  const terminalRef = useRef<TerminalPaneHandle>(null);
  const runSessionRef = useRef<RunSessionClient | null>(null);
  
  const examples = useMemo(() => SIMPLES_EXAMPLES, []);

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

  const handleLoadExample = (example: Example) => {
    const editor = editorRef.current;
    if (editor) {
      editor.setValue(example.code);
    }
  }

  return (
    <div id="ide-shell" className="ide-container">
      <Toolbar
        status={status}
        onRun={handleRun}
        onStop={() => {
          runSessionRef.current?.stop();
        }}
        onLogout={onLogout}
        onExampleSelect={handleLoadExample}
        examples={examples}
      />
      <PanelGroup direction="horizontal" className="ide-panel-group">
        <Panel defaultSize={60} minSize={30}>
          <div className="editor-area ide-editor">
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
      <div className="scanlines"></div>
    </div>
  );
}
