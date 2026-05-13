import importlib
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class WebSocketScaffoldTest(unittest.TestCase):
    def test_backend_requirements_include_flask_sock(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("flask-sock==", content)

    def test_backend_ws_module_can_be_imported(self):
        module = importlib.import_module("backend.ws")
        self.assertIsNotNone(module)


if __name__ == "__main__":
    unittest.main()
