import Editor from "@monaco-editor/react";

interface MonacoEditorPaneProps {
  initialValue?: string;
}

export function MonacoEditorPane({ initialValue = "" }: MonacoEditorPaneProps) {
  function onChange(_value: string | undefined) {
    // handle editor content changes
  }

  return (
    <Editor
      height="90vh"
      defaultLanguage="python"
      defaultValue={initialValue}
      onChange={onChange}
    />
  );
}
