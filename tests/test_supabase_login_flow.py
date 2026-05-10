import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SupabaseLoginUiTest(unittest.TestCase):
    def test_login_ui_and_public_config_exist(self):
        required = [
            ROOT / "frontend" / "index.html",
            ROOT / "frontend" / "config.js",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_login_page_has_email_password_and_ide_shell(self):
        content = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        self.assertIn('type="email"', content)
        self.assertIn('type="password"', content)
        self.assertIn('id="login-form"', content)
        self.assertIn('id="ide-shell"', content)
        self.assertIn("IDE access granted", content)

    def test_login_page_includes_login_screen_marker(self):
        content = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="login-screen"', content)

    def test_login_page_script_has_matching_file(self):
        content = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        self.assertIn('./app.js', content)
        self.assertTrue((ROOT / "frontend" / "app.js").exists())

    def test_public_frontend_config_exposes_supabase_url_and_anon_key(self):
        content = (ROOT / "frontend" / "config.js").read_text(encoding="utf-8")
        self.assertIn("SUPABASE_URL", content)
        self.assertIn("SUPABASE_ANON_KEY", content)


if __name__ == "__main__":
    unittest.main()
