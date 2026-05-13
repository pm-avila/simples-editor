import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class TerminalXtermIntegrationTest(unittest.TestCase):
    def test_frontend_package_json_declares_xterm_dependencies(self):
        package_json = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        dependencies = package_json.get("dependencies", {})
        self.assertIn("xterm", dependencies)
        self.assertIn("xterm-addon-fit", dependencies)

    def test_terminal_pane_imports_xterm_and_fit_addon(self):
        source = (ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx").read_text(
            encoding="utf-8"
        )
        self.assertIn('import { Terminal } from "xterm";', source)
        self.assertIn('import { FitAddon } from "xterm-addon-fit";', source)

    def test_terminal_pane_exposes_forward_ref_and_imperative_handle_api(self):
        source = (ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx").read_text(
            encoding="utf-8"
        )
        self.assertIn("forwardRef", source)
        self.assertIn("useImperativeHandle", source)
        self.assertRegex(source, re.compile(r"export\s+type\s+TerminalPaneHandle\s*=\s*{"))
        self.assertRegex(source, re.compile(r"write:\s*\(data:\s*string\)\s*=>\s*void"))
        self.assertRegex(source, re.compile(r"clear:\s*\(\)\s*=>\s*void"))
        self.assertRegex(source, re.compile(r"focus:\s*\(\)\s*=>\s*void"))
        self.assertRegex(source, re.compile(r"onData\??:\s*\(data:\s*string\)\s*=>\s*void"))


if __name__ == "__main__":
    unittest.main()
