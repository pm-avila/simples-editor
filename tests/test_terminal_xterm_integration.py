import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class TerminalXtermIntegrationTest(unittest.TestCase):
    def test_frontend_package_json_declares_xterm_dependencies(self):
        package_json = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        dependencies = package_json.get("dependencies", {})
        self.assertIn("xterm", dependencies)
        self.assertIn("xterm-addon-fit", dependencies)


if __name__ == "__main__":
    unittest.main()
