import Editor from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { registerSimplesLanguage } from "./simples-language";


interface MonacoEditorPaneProps {
  initialValue?: string;
}


export function MonacoEditorPane({ initialValue = "" }: MonacoEditorPaneProps) {
  function onChange(_value: string | undefined) {
    // handle editor content changes
  }

  function beforeMount(monaco: typeof Monaco) {
    registerSimplesLanguage(monaco);
  }

  return (
    <Editor
      height="90vh"
      beforeMount={beforeMount}
      defaultLanguage="simples"
      defaultValue={initialValue}
      onChange={onChange}
    />
  );
}
