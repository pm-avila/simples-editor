import React from "react";
import { MonacoEditorPane } from "./monaco-editor-pane";

export function IdeShell() {
  return (
    <div id="ide-shell">
      <MonacoEditorPane />
    </div>
  );
}
