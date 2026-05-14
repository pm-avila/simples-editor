# Issue #80: Integrar Compilador Real do SIMPLES — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the stub SIMPLES compiler with the real compiler from `simples-compiler` repository, enabling E2E execution of programs with I/O (`escreva`, `escreval`).

**Architecture:** Update backend Dockerfile to clone and compile `simples-compiler` real during build. Remove stub directory. Refactor tests from mocks to real compiler execution. Add E2E integration tests. Update documentation.

**Tech Stack:** Docker, Git, Python subprocess, pytest, unittest, C compiler (gcc), nasm, ld

---

## File Structure

**Modified Files:**
- `backend/Dockerfile` — Add git + compiler clone/build
- `tests/test_compile_endpoint.py` — Remove subprocess mocks
- `tests/test_ws_run_auth.py` — Remove compile_simples mocks (success cases)
- `backend/compiler.py` — Add startup validation warning (optional)
- `README.md` — Add compiler integration mention
- `docs/SETUP.md` or create new — Dev setup instructions

**New Files:**
- `tests/test_real_compiler_integration.py` — E2E tests with real compiler
- `backend/README.md` — Backend-specific docs

**Deleted Files:**
- `backend/simples-compiler/` — Entire directory (stub)

---

## Task 1: Update Backend Dockerfile

**Files:**
- Modify: `backend/Dockerfile`

- [ ] **Step 1: Read current Dockerfile**

```bash
cat backend/Dockerfile
```

Expected output: Shows Ubuntu 24.04 base, toolchain setup, stub compiler reference.

- [ ] **Step 2: Update Dockerfile to add git and clone real compiler**

Replace the entire Dockerfile with:

```dockerfile
# Funciona em x86_64 (dev local) e ARM64 (Oracle Cloud Ampere A1)
FROM ubuntu:24.04

# Toolchain cross-target i386 + Python + Git
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      nasm \
      binutils-i686-linux-gnu \
      python3 \
      python3-pip \
      ca-certificates \
      curl \
      git \
    && rm -rf /var/lib/apt/lists/*

# Clone and build the real SIMPLES compiler
RUN git clone https://github.com/pm-avila/simples-compiler /tmp/compiler && \
    cd /tmp/compiler && \
    make && \
    cp simplesc /usr/local/bin/simplesc && \
    rm -rf /tmp/compiler

# Backend Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --break-system-packages -r requirements.txt

COPY . ./backend

EXPOSE 5000

CMD ["python3", "-m", "backend.app"]
```

- [ ] **Step 3: Verify Dockerfile syntax**

```bash
docker build --dry-run backend/ 2>&1 | head -20
```

Or just inspect: `cat backend/Dockerfile | grep -E "^(FROM|RUN|COPY|EXPOSE|CMD)"` should show clean structure.

- [ ] **Step 4: Commit**

```bash
git add backend/Dockerfile
git commit -m "feat: update Dockerfile to clone and build real simples-compiler"
```

---

## Task 2: Remove Stub Compiler Directory

**Files:**
- Delete: `backend/simples-compiler/` (entire directory)

- [ ] **Step 1: List stub directory contents**

```bash
ls -la backend/simples-compiler/
```

Expected: Shows simplesc.c, Makefile, README.md, or similar stub files.

- [ ] **Step 2: Remove directory**

```bash
rm -rf backend/simples-compiler/
```

- [ ] **Step 3: Verify removal**

```bash
ls backend/simples-compiler/ 2>&1
```

Expected: `ls: cannot access 'backend/simples-compiler/': No such file or directory`

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: remove stub simples-compiler directory"
```

---

## Task 3: Create E2E Compiler Integration Tests

**Files:**
- Create: `tests/test_real_compiler_integration.py`

- [ ] **Step 1: Create test file with complete content**

```python
"""
Integration tests for real SIMPLES compiler.

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_real_compiler_integration -v

Tests compile and execute real SIMPLES programs (without leia).
Requires /usr/local/bin/simplesc to be available.
"""
import os
import subprocess
import tempfile
import unittest
from backend.compiler import compile_simples


class TestRealCompilerIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Check if compiler is available."""
        cls.has_compiler = os.path.exists("/usr/local/bin/simplesc")

    @unittest.skipIf(not hasattr(TestRealCompilerIntegration, "has_compiler") or not TestRealCompilerIntegration.has_compiler,
                     "simplesc not available")
    def test_simple_output_program_compiles_and_runs(self):
        """Program with escreva generates valid assembly and runs."""
        code = """programa demo
inteiro x;
inicio
  x := 42;
  escreva x;
fim
"""
        result = compile_simples(code)
        self.assertTrue(result["ok"], f"Compilation failed: {result}")
        nasm = result["nasm"]
        
        # Verify NASM is not empty and contains expected sections
        self.assertIn("section", nasm.lower())
        self.assertGreater(len(nasm), 50)  # Should be substantial NASM code
        
        # Compile NASM to binary and execute
        with tempfile.TemporaryDirectory() as tmpdir:
            asm_path = os.path.join(tmpdir, "prog.asm")
            obj_path = os.path.join(tmpdir, "prog.o")
            bin_path = os.path.join(tmpdir, "prog")
            
            with open(asm_path, "w") as f:
                f.write(nasm)
            
            # Assemble
            nasm_result = subprocess.run(
                ["nasm", "-f", "elf32", asm_path, "-o", obj_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(nasm_result.returncode, 0,
                           f"nasm failed: {nasm_result.stderr}")
            
            # Link
            ld_result = subprocess.run(
                ["ld", "-m", "elf_i386", obj_path, "-o", bin_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(ld_result.returncode, 0,
                           f"ld failed: {ld_result.stderr}")
            
            # Execute
            exec_result = subprocess.run(
                [bin_path],
                capture_output=True,
                text=True,
                timeout=2
            )
            # Program should exit cleanly (42 in output or exit code 0)
            # Exact output depends on how compiler generates code
            output_combined = exec_result.stdout + " " + str(exec_result.returncode)
            self.assertIn("42", output_combined,
                        f"Expected 42 in output. Got: stdout={exec_result.stdout}, returncode={exec_result.returncode}")

    @unittest.skipIf(not hasattr(TestRealCompilerIntegration, "has_compiler") or not TestRealCompilerIntegration.has_compiler,
                     "simplesc not available")
    def test_escreval_program_compiles(self):
        """Program with escreval compiles successfully."""
        code = """programa test
inteiro n;
inicio
  n := 100;
  escreval n;
fim
"""
        result = compile_simples(code)
        self.assertTrue(result["ok"], f"Compilation failed: {result}")
        self.assertIn("section", result["nasm"].lower())

    @unittest.skipIf(not hasattr(TestRealCompilerIntegration, "has_compiler") or not TestRealCompilerIntegration.has_compiler,
                     "simplesc not available")
    def test_invalid_program_reports_error(self):
        """Invalid program returns structured error."""
        code = """programa broken
inteiro;
inicio
  x := 1
fim
"""
        result = compile_simples(code)
        self.assertFalse(result["ok"])
        self.assertIn("error", result)
        error = result["error"]
        self.assertIn("phase", error)
        self.assertIn("line", error)
        self.assertIn("column", error)
        self.assertIn("message", error)

    @unittest.skipIf(not hasattr(TestRealCompilerIntegration, "has_compiler") or not TestRealCompilerIntegration.has_compiler,
                     "simplesc not available")
    def test_multiple_statements_program(self):
        """Program with multiple statements compiles."""
        code = """programa calc
inteiro a, b, c;
inicio
  a := 10;
  b := 20;
  c := a + b;
  escreva c;
fim
"""
        result = compile_simples(code)
        self.assertTrue(result["ok"], f"Compilation failed: {result}")
        self.assertIn("section", result["nasm"].lower())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests to verify they execute (will skip if compiler missing)**

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples && \
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_real_compiler_integration -v
```

Expected: Either tests run and pass (if compiler available) or tests skip with "simplesc not available".

- [ ] **Step 3: Commit**

```bash
git add tests/test_real_compiler_integration.py
git commit -m "feat: add E2E integration tests for real compiler"
```

---

## Task 4: Refactor test_compile_endpoint.py — Remove Subprocess Mocks

**Files:**
- Modify: `tests/test_compile_endpoint.py:1-100` (check current state first)

- [ ] **Step 1: Read current test file**

```bash
head -60 tests/test_compile_endpoint.py
```

Understand current mock setup and identify success-case tests that use `_mock_success()`.

- [ ] **Step 2: Remove mock helper functions (keep only error helpers)**

Find and remove the `_mock_success()` function (used for mocking success). Keep `_mock_failure()` for error cases.

Look for:
```python
def _mock_success(nasm_content):
    """Return a side_effect that makes simplesc write nasm_content and exit 0."""
    def fake_run(cmd, capture_output, text, timeout):
        output_path = cmd[cmd.index("-o") + 1]
        with open(output_path, "w") as f:
            f.write(nasm_content)
        proc = MagicMock()
        proc.returncode = 0
        proc.stderr = ""
        return proc
    return fake_run
```

Delete this entire function.

- [ ] **Step 3: Update success tests to call real compiler (remove @patch decorator)**

For each test that previously used `_mock_success()`:

BEFORE:
```python
def test_post_compile_returns_nasm_on_success(self):
    with patch("backend.compiler.subprocess.run", side_effect=_mock_success(SAMPLE_NASM)):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
            ...
        )
```

AFTER (remove mock, call real):
```python
def test_post_compile_returns_nasm_on_success(self):
    resp = self.client.post(
        "/api/compile",
        data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
        ...
    )
```

Do this for all success tests. Keep error tests as they are (they use `_mock_failure()`).

- [ ] **Step 4: Run tests to verify they work or skip gracefully**

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples && \
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_compile_endpoint -v 2>&1 | head -50
```

Expected: Tests pass (if compiler available) or some may fail/error (note which ones, we'll address).

- [ ] **Step 5: Commit**

```bash
git add tests/test_compile_endpoint.py
git commit -m "refactor: remove subprocess mocks from compile endpoint tests"
```

---

## Task 5: Refactor test_ws_run_auth.py — Remove Compile_Simples Mocks (Success Cases)

**Files:**
- Modify: `tests/test_ws_run_auth.py` (search for compile_simples mocks)

- [ ] **Step 1: Identify all mocks of compile_simples in test_ws_run_auth.py**

```bash
grep -n "compile_simples" tests/test_ws_run_auth.py | head -20
```

Look for patterns like:
```python
@patch("backend.ws.run_session.compile_simples", return_value={"ok": True, "nasm": "; stub\n"})
```

- [ ] **Step 2: Remove mocks from SUCCESS test cases**

For tests that patch `compile_simples` with success (`{"ok": True, ...}`), remove the `@patch` decorator and the mock parameter.

BEFORE:
```python
@patch("backend.ws.run_session.compile_simples", return_value={"ok": True, "nasm": "; stub\n"})
def test_run_success(self, mock_compile):
    ...
```

AFTER:
```python
def test_run_success(self):
    ...
```

Keep mocks ONLY for:
- Auth failure tests (mock `compile_simples` or other services as needed)
- Timeout tests (mock to simulate timeout)
- Other error scenarios

- [ ] **Step 3: Run tests to see results**

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples && \
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ws_run_auth -v 2>&1 | head -100
```

Expected: Some tests pass, some may fail if compiler not available (note failures).

- [ ] **Step 4: Commit**

```bash
git add tests/test_ws_run_auth.py
git commit -m "refactor: remove compile_simples mocks from WS run auth tests (success cases)"
```

---

## Task 6: Add Compiler Validation at Startup (Optional but Recommended)

**Files:**
- Modify: `backend/compiler.py:1-20` (add logging at module import)

- [ ] **Step 1: Read current compiler.py header**

```bash
head -30 backend/compiler.py
```

- [ ] **Step 2: Add startup warning if compiler missing**

Insert after imports in `backend/compiler.py`:

```python
import logging

SIMPLESC_BIN = os.environ.get("SIMPLESC_BIN", "/usr/local/bin/simplesc")

if not os.path.exists(SIMPLESC_BIN):
    logging.warning(f"simplesc compiler not found at {SIMPLESC_BIN}")
```

If logging is already imported, just add the warning check.

- [ ] **Step 3: Verify no syntax errors**

```bash
python3 -m py_compile backend/compiler.py && echo "OK"
```

- [ ] **Step 4: Commit**

```bash
git add backend/compiler.py
git commit -m "feat: add startup warning if simplesc compiler missing"
```

---

## Task 7: Create Backend README

**Files:**
- Create: `backend/README.md`

- [ ] **Step 1: Create file with content**

```markdown
# Backend

Backend Flask application that:
- Compiles SIMPLES source code to NASM assembly
- Executes compiled binaries in a sandboxed environment
- Manages WebSocket connections for interactive terminal sessions

## Build

The backend is built in a Docker container. The Dockerfile:
- Uses `ubuntu:24.04` base image with C toolchain (gcc, nasm, ld, binutils)
- Clones and compiles the real SIMPLES compiler from https://github.com/pm-avila/simples-compiler
- Installs the `simplesc` binary to `/usr/local/bin/simplesc`
- Sets up Python environment with Flask and dependencies

**Build will fail-fast** if the compiler clone or make fails (no fallback).

## Compiler

The backend expects the SIMPLES compiler binary at `/usr/local/bin/simplesc`.

**Invocation:**
```bash
simplesc <source.simples> -o <output.asm>
```

**Outputs:**
- Exit code 0: Success — output file `.asm` is written
- Exit code != 0: Error — stderr contains structured error: `<line>:<col>: erro [phase]: message`

**Phases:**
- `lexer` — Lexical analysis error
- `parser` — Syntax error
- `semantic` — Semantic analysis error
- `compile` — General compilation error

## Development

See `docs/SETUP.md` for local development setup.

## Testing

Run backend tests:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover tests -v
```

Integration tests require `/usr/local/bin/simplesc` to be available. Tests will skip gracefully if missing.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_real_compiler_integration -v
```
```

- [ ] **Step 2: Commit**

```bash
git add backend/README.md
git commit -m "docs: add backend README with compiler and build information"
```

---

## Task 8: Update Root README and Create/Update SETUP.md

**Files:**
- Modify: `README.md` (add compiler integration section)
- Create or Modify: `docs/SETUP.md` (add local dev setup for compiler)

- [ ] **Step 1: Read current README.md**

```bash
head -50 README.md
```

- [ ] **Step 2: Add compiler integration section to README.md**

Find an appropriate location (typically after the architecture or getting-started section) and add:

```markdown
## Compiler Integration

This project uses the real SIMPLES compiler from [pm-avila/simples-compiler](https://github.com/pm-avila/simples-compiler).

The backend compiles SIMPLES source code to NASM assembly (`simplesc`) and executes binaries in a sandboxed environment.

For detailed information about the backend, see [`backend/README.md`](./backend/README.md).
For local development setup, see [`docs/SETUP.md`](./docs/SETUP.md).
```

- [ ] **Step 3: Create or update docs/SETUP.md with local dev compiler setup**

Create `docs/SETUP.md` (if doesn't exist) with section:

```markdown
# Development Setup

## Prerequisites

### Compiler (Local Dev)

For local development, you need the real SIMPLES compiler:

1. **Clone and build the compiler:**

   ```bash
   git clone https://github.com/pm-avila/simples-compiler /tmp/simples-compiler
   cd /tmp/simples-compiler
   make
   sudo cp simplesc /usr/local/bin/simplesc
   ```

   (Requires `sudo` to install to `/usr/local/bin`. Alternatively, set `SIMPLESC_BIN` environment variable to a local path.)

2. **Verify installation:**

   ```bash
   simplesc --help
   # or check existence:
   test -f /usr/local/bin/simplesc && echo "OK" || echo "NOT FOUND"
   ```

### Backend

1. **Create Python virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run backend tests:**

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover tests -v
   ```

   If `/usr/local/bin/simplesc` is not available, integration tests will be skipped.

### Docker

To test the full Docker build:

```bash
docker-compose build backend
docker-compose up
```

The backend container will automatically clone and compile the real compiler during the build.
```

- [ ] **Step 4: Verify markdown syntax**

```bash
ls -la docs/SETUP.md README.md && echo "Files exist"
```

- [ ] **Step 5: Commit**

```bash
git add README.md docs/SETUP.md
git commit -m "docs: add compiler integration and local setup documentation"
```

---

## Task 9: Integration Test — Docker Build + Run

**Files:**
- Tested: Everything (whole system)

- [ ] **Step 1: Build backend Docker image**

```bash
cd /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples && \
docker-compose build backend 2>&1 | tail -50
```

Expected: Build succeeds and shows "Successfully tagged" message.

- [ ] **Step 2: Verify simplesc is available in container**

```bash
docker-compose run --rm backend test -f /usr/local/bin/simplesc && echo "Compiler present"
```

Expected: "Compiler present"

- [ ] **Step 3: Run test inside container**

```bash
docker-compose run --rm backend bash -c \
  "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_compile_endpoint.TestCompileEndpointSuccess.test_post_compile_returns_nasm_on_success -v"
```

Expected: Test passes (real compiler working).

- [ ] **Step 4: Spin up full stack and test manually (optional)**

```bash
docker-compose up -d
sleep 5
curl http://localhost:8080 # Check frontend is up
curl http://localhost/api/health # Check backend is up
docker-compose logs backend | grep -i simplesc # Should see startup or check result
docker-compose down
```

- [ ] **Step 5: Commit**

No code changes here, but document any findings:

```bash
git log --oneline | head -10  # Show last 10 commits
```

---

## Self-Review Against Spec

**Spec Coverage:**

1. ✅ **Integração no Docker:** Task 1 (Dockerfile clone + build + install)
2. ✅ **Remover stub:** Task 2 (delete backend/simples-compiler/)
3. ✅ **Atualizar testes existentes:** Task 4 & 5 (remove mocks)
4. ✅ **Novo test file E2E:** Task 3 (test_real_compiler_integration.py)
5. ✅ **Validação em tempo de execução:** Task 6 (startup warning)
6. ✅ **Documentação:** Task 7, 8 (backend/README.md, SETUP.md, raiz README)
7. ✅ **Critérios de aceite:** All covered by tasks

**Placeholder Scan:**
- ✅ No TBD, TODO, or "similar to"
- ✅ All code examples complete
- ✅ All commands with expected output
- ✅ No vague steps

**Type/Name Consistency:**
- ✅ `compile_simples()` used consistently
- ✅ `/usr/local/bin/simplesc` path consistent
- ✅ Error structure `{phase, line, column, message}` consistent

**No Gaps:** All spec requirements mapped to tasks.

---

## Execution Checklist

- [ ] Task 1: Dockerfile updated
- [ ] Task 2: Stub removed
- [ ] Task 3: E2E tests created
- [ ] Task 4: test_compile_endpoint.py refactored
- [ ] Task 5: test_ws_run_auth.py refactored
- [ ] Task 6: Startup warning added
- [ ] Task 7: backend/README.md created
- [ ] Task 8: Root README + SETUP.md updated
- [ ] Task 9: Full Docker build + integration test

---

## Notes

- **Compiler Availability:** Tests skip gracefully with `@unittest.skipIf` if `/usr/local/bin/simplesc` is missing. This allows local dev without compiler installed (though integration tests won't run).
- **Fail-Fast Philosophy:** Docker build fails immediately if git clone or make fails. No hidden retries or fallbacks.
- **Timelines:** Build will take 1-2 minutes (compiler compilation). First run may be slower.
- **Git Clone in Docker:** Uses latest `main`/`master` from simples-compiler repo (user preference). Network failures will fail the build, which is intentional.

---

## Commit Summary

After all tasks:
```bash
git log --oneline -10
```

You should see commits like:
1. Update Dockerfile
2. Remove stub
3. Add E2E tests
4. Refactor compile endpoint tests
5. Refactor WS run auth tests
6. Add startup warning
7. Add backend README
8. Update docs
