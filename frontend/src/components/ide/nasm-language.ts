import type * as Monaco from "monaco-editor";

export const NASM_LANGUAGE_ID = "nasm";

export function registerNasmLanguage(monaco: typeof Monaco): void {
  if (monaco.languages.getLanguages().some((l) => l.id === NASM_LANGUAGE_ID)) return;

  monaco.languages.register({ id: NASM_LANGUAGE_ID, extensions: [".asm", ".nasm"] });

  monaco.languages.setMonarchTokensProvider(NASM_LANGUAGE_ID, {
    defaultToken: "",
    tokenPostfix: ".nasm",

    keywords: [
      "section", "global", "extern", "bits", "use16", "use32", "use64",
      "org", "align", "times", "db", "dw", "dd", "dq", "dt", "resb", "resw",
      "resd", "resq", "rest", "equ", "incbin", "struc", "endstruc", "istruc", "iend",
      "at", "common", "cpu", "float",
    ],

    registers: [
      "eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp",
      "ax", "bx", "cx", "dx", "si", "di", "sp", "bp",
      "al", "bl", "cl", "dl", "ah", "bh", "ch", "dh",
      "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rsp", "rbp",
      "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15",
      "cs", "ds", "es", "fs", "gs", "ss",
      "eflags", "rflags", "eip", "rip",
    ],

    instructions: [
      "mov", "add", "sub", "mul", "imul", "div", "idiv", "inc", "dec",
      "and", "or", "xor", "not", "neg", "shl", "shr", "sal", "sar",
      "cmp", "test", "jmp", "je", "jne", "jz", "jnz", "jg", "jge",
      "jl", "jle", "ja", "jae", "jb", "jbe", "call", "ret", "retn", "retf",
      "push", "pop", "pusha", "popa", "pushad", "popad", "pushf", "popf",
      "lea", "xchg", "nop", "int", "iret", "iretd", "hlt", "clc", "stc",
      "cli", "sti", "cld", "std", "rep", "repe", "repz", "repne", "repnz",
      "movsb", "movsw", "movsd", "lodsb", "lodsw", "lodsd",
      "stosb", "stosw", "stosd", "scasb", "scasw", "scasd",
      "cmpsb", "cmpsw", "cmpsd", "in", "out", "outs", "ins",
      "enter", "leave", "syscall", "sysenter", "sysexit",
      "cbw", "cwd", "cdq", "cwde", "movzx", "movsx",
      "setg", "setge", "setl", "setle", "sete", "setne",
      "rol", "ror", "rcl", "rcr", "adc", "sbb",
    ],

    sizeSpecifiers: ["byte", "word", "dword", "qword", "ptr", "near", "far", "short"],

    tokenizer: {
      root: [
        // Comments
        [/;.*$/, "comment"],

        // Labels (identifier followed by colon)
        [/^[a-zA-Z_?][a-zA-Z0-9_?]*:/, "tag"],
        [/\.[a-zA-Z_][a-zA-Z0-9_]*:/, "tag"],

        // Local labels and dot-prefixed identifiers
        [/\.[a-zA-Z_][a-zA-Z0-9_]*/, "type.identifier"],

        // Section names (after section keyword)
        [/\.(data|text|bss|rodata|init|fini|plt|got)/, "string"],

        // Numbers
        [/0[xX][0-9a-fA-F]+/, "number.hex"],
        [/0[bB][01]+/, "number.binary"],
        [/0[oO][0-7]+/, "number.octal"],
        [/-?\d+/, "number"],

        // Strings
        [/'([^'\\]|\\.)*'/, "string"],
        [/"([^"\\]|\\.)*"/, "string"],
        [/`([^`\\]|\\.)*`/, "string"],

        // Whitespace
        [/[ \t\r\n]+/, "white"],

        // Identifiers / keywords / registers
        [/[a-zA-Z_][a-zA-Z0-9_]*/, {
          cases: {
            "@keywords": "keyword",
            "@instructions": "keyword.control",
            "@registers": "variable.predefined",
            "@sizeSpecifiers": "type",
            "@default": "identifier",
          },
        }],

        // Operators and punctuation
        [/[+\-*/%&|^~<>]/, "operator"],
        [/[[\](),]/, "delimiter"],
      ],
    },
  });
}
