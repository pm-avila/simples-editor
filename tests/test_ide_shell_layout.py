import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class IdePaneContractTest(unittest.TestCase):
    def test_nasm_pane_module_exists(self):
        path = ROOT / "frontend" / "src" / "components" / "ide" / "nasm-pane.tsx"
        self.assertTrue(path.exists(), f"missing: {path}")

    def test_terminal_pane_module_exists(self):
        path = ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx"
        self.assertTrue(path.exists(), f"missing: {path}")

    def test_nasm_pane_has_header(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "nasm-pane.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("NASM x32", content)

    def test_terminal_pane_has_label(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("Terminal", content)


if __name__ == "__main__":
    unittest.main()
