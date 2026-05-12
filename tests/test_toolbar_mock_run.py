import unittest
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
TOOLBAR = ROOT / "frontend/src/components/ide/toolbar.tsx"
IDE_SHELL = ROOT / "frontend/src/components/ide/ide-shell.tsx"
MONACO_PANE = ROOT / "frontend/src/components/ide/monaco-editor-pane.tsx"
NASM_PANE = ROOT / "frontend/src/components/ide/nasm-pane.tsx"
STYLES = ROOT / "frontend/src/styles.css"


class ToolbarMockRunTests(unittest.TestCase):

    def test_toolbar_component_exists(self):
        """toolbar.tsx must export a Toolbar function."""
        src = TOOLBAR.read_text()
        self.assertIn("export function Toolbar", src)

    def test_toolbar_has_run_button(self):
        """Toolbar must render the Run button with toolbar__run-btn class."""
        src = TOOLBAR.read_text()
        self.assertIn("toolbar__run-btn", src)

    def test_toolbar_has_stop_button(self):
        """Toolbar must render the Stop button with toolbar__stop-btn class."""
        src = TOOLBAR.read_text()
        self.assertIn("toolbar__stop-btn", src)

    def test_ide_shell_imports_toolbar(self):
        """IdeShell must import Toolbar."""
        src = IDE_SHELL.read_text()
        self.assertIn("Toolbar", src)

    def test_ide_shell_manages_status_state(self):
        """IdeShell must use useState typed to IdeStatus."""
        src = IDE_SHELL.read_text()
        self.assertIn('useState<IdeStatus>', src)

    def test_ide_shell_status_has_compiling_value(self):
        """IdeShell must reference the 'compiling' status value."""
        src = IDE_SHELL.read_text()
        self.assertIn('"compiling"', src)

    def test_monaco_pane_accepts_readonly_prop(self):
        """MonacoEditorPane must accept a readOnly prop and pass it to Monaco."""
        src = MONACO_PANE.read_text()
        self.assertIn("readOnly", src)

    def test_nasm_pane_accepts_status_prop(self):
        """NasmPane must declare a status prop in its props interface."""
        src = NASM_PANE.read_text()
        self.assertIn("status:", src)

    def test_nasm_pane_shows_mock_message(self):
        """NasmPane must render a 'compilando' placeholder when compiling."""
        src = NASM_PANE.read_text()
        self.assertIn("compilando", src)

    def test_toolbar_css_exists(self):
        """styles.css must define the .toolbar rule."""
        css = STYLES.read_text()
        self.assertIn(".toolbar", css)
