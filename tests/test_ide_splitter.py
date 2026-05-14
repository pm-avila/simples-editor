import unittest
import pathlib
import re

ROOT = pathlib.Path(__file__).parent.parent
IDE_SHELL = ROOT / "frontend/src/components/ide/ide-shell.tsx"
STYLES = ROOT / "frontend/src/styles.css"


class IdeShellSplitterTests(unittest.TestCase):

    def test_ide_shell_imports_panel_group(self):
        """IdeShell must import PanelGroup from react-resizable-panels."""
        src = IDE_SHELL.read_text()
        self.assertIn("PanelGroup", src)
        self.assertIn("react-resizable-panels", src)

    def test_ide_shell_imports_panel_resize_handle(self):
        """IdeShell must import PanelResizeHandle from react-resizable-panels."""
        src = IDE_SHELL.read_text()
        self.assertIn("PanelResizeHandle", src)

    def test_nasm_panel_is_collapsible(self):
        """The NASM Panel must have the collapsible attribute."""
        src = IDE_SHELL.read_text()
        self.assertIn("collapsible", src)

    def test_resize_handle_has_double_click(self):
        """PanelResizeHandle must have an onDoubleClick handler."""
        src = IDE_SHELL.read_text()
        self.assertIn("onDoubleClick", src)

    def test_resize_handle_style_in_css(self):
        """styles.css must define .resize-handle rule."""
        css = STYLES.read_text()
        self.assertIn(".resize-handle", css)

    def test_grid_template_columns_removed_from_ide_shell(self):
        """grid-template-columns must be removed from the #ide-shell rule (replaced by PanelGroup)."""
        css = STYLES.read_text()
        match = re.search(r'#ide-shell\s*\{([^}]*)\}', css)
        self.assertIsNotNone(match, "#ide-shell rule not found in styles.css")
        self.assertNotIn("grid-template-columns", match.group(1))
