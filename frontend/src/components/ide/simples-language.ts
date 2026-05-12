import type * as Monaco from "monaco-editor";

export const SIMPLES_LANGUAGE_ID = "simples";

export const SIMPLES_KEYWORDS = [
  "programa", "inicio", "fim",
  "inteiro", "flutuante", "vazio",
  "se", "entao", "senao", "fimse",
  "enquanto", "fimenquanto",
  "para", "de", "ate", "passo", "faca", "fimpara",
  "leia", "escreva", "escreval",
  "e", "ou", "nao",
  "div",
  "procedimento", "retorna",
] as const;

let isRegistered = false;

export function registerSimplesLanguage(monaco: typeof Monaco) {
  if (isRegistered) {
    return;
  }

  monaco.languages.register({ id: SIMPLES_LANGUAGE_ID });
  monaco.languages.setMonarchTokensProvider(SIMPLES_LANGUAGE_ID, {
    ignoreCase: true,
    keywords: SIMPLES_KEYWORDS,
    operators: ["<-", "+", "-", "*", "div", ">", "<", "=", "<>", ">=", "<="],
    symbols: /[=<>+\-*]+/,
    tokenizer: {
      root: [
        [/[a-zA-Z_]\w*/, { cases: { "@keywords": "keyword", "@default": "identifier" } }],
        [/\d+\.\d+/, "number.float"],
        [/\d+/, "number"],
        [/<-/, "operator"],
        [/@symbols/, { cases: { "@operators": "operator", "@default": "" } }],
        [/[(),;]/, "delimiter"],
        [/\s+/, "white"],
      ],
    },
  });

  isRegistered = true;
}
