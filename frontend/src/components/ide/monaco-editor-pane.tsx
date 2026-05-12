import { forwardRef, useImperativeHandle, useRef } from "react";
import Editor from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { registerSimplesLanguage, SIMPLES_LANGUAGE_ID } from "./simples-language";
import { defineSimplesDarkTheme, SIMPLES_THEME_ID } from "./simples-theme";
import type { CompileError } from "../../lib/compile-api";


export interface MonacoEditorPaneHandle {
  getValue(): string;
  setMarkers(errors: CompileError[]): void;
  clearMarkers(): void;
}

interface MonacoEditorPaneProps {
  initialValue?: string;
  readOnly?: boolean;
}


export const MonacoEditorPane = forwardRef<MonacoEditorPaneHandle, MonacoEditorPaneProps>(
  function MonacoEditorPane({ initialValue = "", readOnly = false }, ref) {
    const monacoRef = useRef<typeof Monaco | null>(null);
    const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);

    useImperativeHandle(ref, () => ({
      getValue() {
        return editorRef.current?.getValue() ?? "";
      },
      setMarkers(errors: CompileError[]) {
        const monaco = monacoRef.current;
        const editor = editorRef.current;
        if (!monaco || !editor) return;
        const model = editor.getModel();
        if (!model) return;
        monaco.editor.setModelMarkers(
          model,
          "simplesc",
          errors.map((err) => ({
            severity: monaco.MarkerSeverity.Error,
            startLineNumber: err.line,
            endLineNumber: err.line,
            startColumn: err.column,
            endColumn: err.column + 1,
            message: err.message,
          }))
        );
      },
      clearMarkers() {
        const monaco = monacoRef.current;
        const editor = editorRef.current;
        if (!monaco || !editor) return;
        const model = editor.getModel();
        if (!model) return;
        monaco.editor.setModelMarkers(model, "simplesc", []);
      },
    }));

    function beforeMount(monaco: typeof Monaco) {
      monacoRef.current = monaco;
      registerSimplesLanguage(monaco);
      defineSimplesDarkTheme(monaco);
    }

    function onMount(editor: Monaco.editor.IStandaloneCodeEditor) {
      editorRef.current = editor;
    }

    return (
      <Editor
        height="100%"
        beforeMount={beforeMount}
        onMount={onMount}
        defaultLanguage={SIMPLES_LANGUAGE_ID}
        defaultValue={initialValue}
        theme={SIMPLES_THEME_ID}
        options={{ readOnly }}
      />
    );
  }
);

