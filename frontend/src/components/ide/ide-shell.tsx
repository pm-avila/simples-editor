import { useRef } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import type { ImperativePanelHandle } from "react-resizable-panels";
import { MonacoEditorPane } from "./monaco-editor-pane";
import { NasmPane } from "./nasm-pane";
import { TerminalPane } from "./terminal-pane";


export function IdeShell() {
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
      <PanelGroup direction="horizontal" className="ide-panel-group">
        <Panel defaultSize={60} minSize={30}>
          <div className="editor-area">
            <MonacoEditorPane />
          </div>
        </Panel>
        <PanelResizeHandle className="resize-handle" onDoubleClick={handleDoubleClick} />
        <Panel ref={nasmPanelRef} defaultSize={40} minSize={20} collapsible>
          <NasmPane />
        </Panel>
      </PanelGroup>
      <div className="terminal-area">
        <TerminalPane />
      </div>
    </div>
  );
}
