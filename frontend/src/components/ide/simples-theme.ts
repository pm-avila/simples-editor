import type * as Monaco from "monaco-editor";


export const SIMPLES_THEME_ID = "simples-dark";

let isDefined = false;

export function defineSimplesDarkTheme(monaco: typeof Monaco) {
  if (isDefined) return;

  monaco.editor.defineTheme(SIMPLES_THEME_ID, {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword",      foreground: "4FC1FF" },
      { token: "number.float", foreground: "FFB347" },
      { token: "number",       foreground: "FFB347" },
      { token: "identifier",   foreground: "D4D4D4" },
      { token: "comment",      foreground: "6A9955", fontStyle: "italic" },
      { token: "operator",     foreground: "D4D4D4" },
      { token: "delimiter",    foreground: "D4D4D4" },
    ],
    colors: {},
  });

  isDefined = true;
}
