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

    def test_config_js_in_public_for_vite_build(self):
        """config.js must live in frontend/public/ so Vite copies it to dist/."""
        public_config = ROOT / "frontend" / "public" / "config.js"
        self.assertTrue(public_config.exists(), "frontend/public/config.js missing – dist/ won't include it")
        content = public_config.read_text(encoding="utf-8")
        self.assertIn("__SUPABASE_URL__", content)
        self.assertIn("__SUPABASE_ANON_KEY__", content)

    def test_app_source_exposes_login_marker(self):
        content = (ROOT / "frontend" / "src" / "app.tsx").read_text(encoding="utf-8")
        self.assertIn("login-screen", content)


class SupabaseLoginFlowScriptTest(unittest.TestCase):
    def test_runtime_config_and_client_are_centralized(self):
        config = (ROOT / "frontend" / "src" / "lib" / "runtime-config.ts").read_text(encoding="utf-8")
        supabase = (ROOT / "frontend" / "src" / "lib" / "supabase.ts").read_text(encoding="utf-8")
        self.assertIn("window.__SUPABASE_URL__", config)
        self.assertIn("window.__SUPABASE_ANON_KEY__", config)
        self.assertIn("createClient", supabase)

    def test_login_component_keeps_existing_markers(self):
        content = (ROOT / "frontend" / "src" / "components" / "auth" / "login-screen.tsx").read_text(encoding="utf-8")
        app = (ROOT / "frontend" / "src" / "app.tsx").read_text(encoding="utf-8")
        self.assertIn('id="login-form"', content)
        self.assertIn('type="email"', content)
        self.assertIn('type="password"', content)
        self.assertIn("signInWithPassword", app)
        self.assertIn("getSession", app)
        self.assertIn("ide-shell", app)


if __name__ == "__main__":
    unittest.main()
