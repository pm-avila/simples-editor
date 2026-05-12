import unittest
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
NASM_PANE = ROOT / "frontend/src/components/ide/nasm-pane.tsx"


class NasmMonacoPaneTests(unittest.TestCase):

    def test_nasm_pane_imports_monaco_editor(self):
        """nasm-pane.tsx must import Editor from @monaco-editor/react."""
        src = NASM_PANE.read_text()
        self.assertIn("@monaco-editor/react", src)
        self.assertIn("Editor", src)

    def test_nasm_pane_uses_asm_language(self):
        """nasm-pane.tsx must set language to asm."""
        src = NASM_PANE.read_text()
        self.assertIn('language="asm"', src)

    def test_nasm_pane_is_readonly(self):
        """nasm-pane.tsx Monaco options must set readOnly: true."""
        src = NASM_PANE.read_text()
        self.assertIn("readOnly: true", src)

    def test_nasm_pane_accepts_value_prop(self):
        """nasm-pane.tsx must declare a value prop in the props interface."""
        src = NASM_PANE.read_text()
        self.assertIn("value?:", src)

    def test_nasm_pane_mock_message_in_monaco(self):
        """nasm-pane.tsx must pass 'compilando' text as Monaco value when compiling."""
        src = NASM_PANE.read_text()
        self.assertIn("compilando", src)
