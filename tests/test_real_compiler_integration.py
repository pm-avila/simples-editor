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


# Check compiler availability at module load time
HAS_COMPILER = os.path.exists("/usr/local/bin/simplesc")


class TestRealCompilerIntegration(unittest.TestCase):

    @unittest.skipIf(not HAS_COMPILER, "simplesc not available")
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

    @unittest.skipIf(not HAS_COMPILER, "simplesc not available")
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

    @unittest.skipIf(not HAS_COMPILER, "simplesc not available")
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

    @unittest.skipIf(not HAS_COMPILER, "simplesc not available")
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
