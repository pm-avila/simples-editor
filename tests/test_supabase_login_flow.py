import importlib.util
import os
import pathlib
import sys
import unittest
import unittest.mock


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_server_module():
    """Import frontend/server.py without executing its __main__ block."""
    spec = importlib.util.spec_from_file_location(
        "frontend_server",
        ROOT / "frontend" / "server.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


class ServerRuntimeConfigTest(unittest.TestCase):
    """server.py must serve /config.js dynamically from environment variables."""

    def setUp(self):
        self._server_mod = _load_server_module()

    def test_default_values_used_when_env_not_set(self):
        env = {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY")}
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            body = self._server_mod._build_config_js().decode()
        self.assertIn("https://example.supabase.co", body)
        self.assertIn("dev-anon-key", body)

    def test_env_vars_override_defaults(self):
        with unittest.mock.patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://my-project.supabase.co", "SUPABASE_ANON_KEY": "my-real-key"},
        ):
            body = self._server_mod._build_config_js().decode()
        self.assertIn("https://my-project.supabase.co", body)
        self.assertIn("my-real-key", body)
        self.assertNotIn("example.supabase.co", body)
        self.assertNotIn("dev-anon-key", body)

    def test_output_assigns_global_window_variables(self):
        with unittest.mock.patch.dict(os.environ, {"SUPABASE_URL": "https://u.co", "SUPABASE_ANON_KEY": "k"}):
            body = self._server_mod._build_config_js().decode()
        self.assertIn("window.__SUPABASE_URL__", body)
        self.assertIn("window.__SUPABASE_ANON_KEY__", body)

    def test_server_has_do_get_override(self):
        """Handler.do_GET must exist so /config.js is intercepted before file lookup."""
        self.assertTrue(
            hasattr(self._server_mod.Handler, "do_GET"),
            "Handler must define do_GET to intercept /config.js",
        )


if __name__ == "__main__":
    unittest.main()
