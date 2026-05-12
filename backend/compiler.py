"""
Compiler service — wraps simplesc invocation via subprocess.
"""
import os
import re
import subprocess
import tempfile

SIMPLESC_BIN = os.environ.get("SIMPLESC_BIN", "/usr/local/bin/simplesc")
COMPILE_TIMEOUT = int(os.environ.get("COMPILE_TIMEOUT", "15"))

_ERROR_RE = re.compile(r"^(\d+):(\d+):\s*(?:erro:\s*)?(.+)$", re.MULTILINE)


def compile_simples(code: str) -> dict:
    """Compile SIMPLES source to NASM assembly.

    Returns:
        {"ok": True,  "nasm": "<str>"}
        {"ok": False, "error": {"phase": "compile", "line": N, "column": N, "message": "..."}}
    """
    with tempfile.TemporaryDirectory(prefix="sim-") as tmpdir:
        src_path = os.path.join(tmpdir, "programa.simples")
        asm_path = os.path.join(tmpdir, "programa.asm")

        with open(src_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            result = subprocess.run(
                [SIMPLESC_BIN, src_path, "-o", asm_path],
                capture_output=True,
                text=True,
                timeout=COMPILE_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": {
                    "phase": "compile",
                    "line": 0,
                    "column": 0,
                    "message": "timeout: compilação excedeu o limite de tempo",
                },
            }

        if result.returncode != 0:
            return {"ok": False, "error": _parse_compiler_error(result.stderr)}

        try:
            with open(asm_path, "r", encoding="utf-8") as f:
                nasm = f.read()
        except (FileNotFoundError, OSError):
            return {
                "ok": False,
                "error": {
                    "phase": "compile",
                    "line": 0,
                    "column": 0,
                    "message": "compilation failed: output file not produced",
                },
            }

        return {"ok": True, "nasm": nasm}


def _parse_compiler_error(stderr: str) -> dict:
    """Parse compiler stderr line into a structured error dict."""
    match = _ERROR_RE.search(stderr)
    if match:
        return {
            "phase": "compile",
            "line": int(match.group(1)),
            "column": int(match.group(2)),
            "message": match.group(3).strip(),
        }
    return {
        "phase": "compile",
        "line": 0,
        "column": 0,
        "message": stderr.strip() or "compilation failed",
    }
