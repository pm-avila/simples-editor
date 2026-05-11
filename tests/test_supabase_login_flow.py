import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SupabaseLoginUiTest(unittest.TestCase):
    def test_frontend_react_entrypoints_exist(self):
        required = [
            ROOT / "frontend" / "index.html",
            ROOT / "frontend" / "config.js",
            ROOT / "frontend" / "package.json",
            ROOT / "frontend" / "src" / "main.tsx",
            ROOT / "frontend" / "src" / "app.tsx",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_app_source_exposes_login_marker(self):
        content = (ROOT / "frontend" / "src" / "app.tsx").read_text(encoding="utf-8")
        self.assertIn("login-screen", content)


if __name__ == "__main__":
    unittest.main()
