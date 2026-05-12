import Editor from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { registerSimplesLanguage, SIMPLES_LANGUAGE_ID } from "./simples-language";
import { defineSimplesDarkTheme, SIMPLES_THEME_ID } from "./simples-theme";


interface MonacoEditorPaneProps {
  initialValue?: string;
}


export function MonacoEditorPane({ initialValue = "" }: MonacoEditorPaneProps) {
  function onChange(_value: string | undefined) {
    // handle editor content changes
  }

  function beforeMount(monaco: typeof Monaco) {
    registerSimplesLanguage(monaco);
    defineSimplesDarkTheme(monaco);
  }

  return (
    <Editor
      height="100%"
      beforeMount={beforeMount}
      defaultLanguage={SIMPLES_LANGUAGE_ID}
      defaultValue={initialValue}
      theme={SIMPLES_THEME_ID}
      onChange={onChange}
    />
  );
}
