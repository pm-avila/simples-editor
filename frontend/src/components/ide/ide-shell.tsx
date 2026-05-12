import { useState, useRef } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import type { ImperativePanelHandle } from "react-resizable-panels";
import { MonacoEditorPane } from "./monaco-editor-pane";
import { NasmPane } from "./nasm-pane";
import { TerminalPane } from "./terminal-pane";
import { Toolbar } from "./toolbar";

type IdeStatus = "idle" | "compiling";


export function IdeShell() {
  const [status, setStatus] = useState<IdeStatus>("idle");
  const nasmPanelRef = useRef<ImperativePanelHandle>(null);

  function handleDoubleClick() {
    const panel = nasmPanelRef.current;
    if (!panel) return;
    if (panel.isCollapsed()) {
      panel.expand();
    } else {
      panel.collapse();
    }
  }

  return (
    <div id="ide-shell">
      <Toolbar
        status={status}
        onRun={() => setStatus("compiling")}
        onStop={() => setStatus("idle")}
      />
      <PanelGroup direction="horizontal" className="ide-panel-group">
        <Panel defaultSize={60} minSize={30}>
          <div className="editor-area">
            <MonacoEditorPane readOnly={status === "compiling"} />
          </div>
        </Panel>
        <PanelResizeHandle className="resize-handle" onDoubleClick={handleDoubleClick} />
        <Panel ref={nasmPanelRef} defaultSize={40} minSize={20} collapsible>
          <NasmPane status={status} />
        </Panel>
      </PanelGroup>
      <div className="terminal-area">
        <TerminalPane />
      </div>
    </div>
  );
}
