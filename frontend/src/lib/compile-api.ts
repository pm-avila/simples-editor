/** Structured compiler error as returned by POST /api/compile */
export interface CompileError {
  phase: "lexer" | "parser" | "semantic" | "compile";
  line: number;
  column: number;
  message: string;
}

/** Success result from POST /api/compile */
export interface CompileSuccess {
  nasm: string;
}

type CompileResult =
  | { ok: true; nasm: string }
  | { ok: false; error: CompileError };

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function compileCode(code: string): Promise<CompileResult> {
  const response = await fetch(`${API_BASE}/api/compile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (response.ok) {
    const data = (await response.json()) as CompileSuccess;
    return { ok: true, nasm: data.nasm };
  }

  if (response.status === 422) {
    const data = (await response.json()) as { error: CompileError };
    return { ok: false, error: data.error };
  }

  return {
    ok: false,
    error: {
      phase: "compile",
      line: 0,
      column: 0,
      message: `Unexpected server error (HTTP ${response.status})`,
    },
  };
}
