import Editor from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { registerSimplesLanguage, SIMPLES_LANGUAGE_ID } from "./simples-language";


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
      defaultLanguage={SIMPLES_LANGUAGE_ID}
      defaultValue={initialValue}
      onChange={onChange}
    />
  );
}
