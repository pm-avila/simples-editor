import pathlib
import unittest
import importlib.util


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SupabaseFoundationFilesTest(unittest.TestCase):
    def test_env_and_supabase_contract_files_exist(self):
        required = [
            ROOT / ".env.example",
            ROOT / "supabase" / "config.toml",
            ROOT / "backend" / "requirements.txt",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_env_example_declares_required_supabase_variables(self):
        content = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("SUPABASE_URL=", content)
        self.assertIn("SUPABASE_ANON_KEY=", content)
        self.assertNotIn("SUPABASE_JWT_SECRET=", content)

    def test_supabase_config_enables_auth_for_local_project(self):
        content = (ROOT / "supabase" / "config.toml").read_text(encoding="utf-8")
        self.assertIn("project_id =", content)
        self.assertIn("[auth]", content)
        self.assertIn("site_url =", content)
        self.assertIn("enable_signup =", content)

    def test_supabase_config_matches_minimal_task_one_content(self):
        content = (ROOT / "supabase" / "config.toml").read_text(encoding="utf-8")
        expected = (
            'project_id = "simples-editor"\n'
            '[auth]\n'
            'enabled = true\n'
            'site_url = "http://localhost"\n'
            'additional_redirect_urls = ["http://localhost"]\n'
            'jwt_expiry = 3600\n'
            'enable_signup = true\n'
            'enable_anonymous_sign_ins = false\n'
        )
        self.assertEqual(expected, content)

    def test_backend_requirements_prepare_local_jwt_validation(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("PyJWT==", content)


class BackendAuthConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = ROOT / "backend" / "auth_config.py"
        spec = importlib.util.spec_from_file_location("backend.auth_config", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_load_supabase_auth_config_returns_expected_fields(self):
        config = self.module.load_supabase_auth_config(
            {
                "SUPABASE_URL": "https://demo.supabase.co",
                "SUPABASE_ANON_KEY": "anon",
                "SUPABASE_JWT_SECRET": "secret",
            }
        )
        self.assertEqual(config.url, "https://demo.supabase.co")
        self.assertEqual(config.anon_key, "anon")
        self.assertEqual(config.jwt_secret, "secret")

    def test_load_supabase_auth_config_allows_missing_jwt_secret(self):
        config = self.module.load_supabase_auth_config(
            {
                "SUPABASE_URL": "https://demo.supabase.co",
                "SUPABASE_ANON_KEY": "anon",
            }
        )
        self.assertEqual(config.url, "https://demo.supabase.co")
        self.assertEqual(config.anon_key, "anon")
        self.assertIsNone(config.jwt_secret)

    def test_auth_model_summary_explains_local_jwt_validation(self):
        summary = self.module.auth_model_summary()
        self.assertIn("auth.users", summary)
        self.assertIn("JWT", summary)
        self.assertIn("without querying the database", summary)

    def test_load_supabase_auth_config_rejects_blank_values(self):
        with self.assertRaises(ValueError):
            self.module.load_supabase_auth_config(
                {
                    "SUPABASE_URL": "   ",
                    "SUPABASE_ANON_KEY": "anon",
                    "SUPABASE_JWT_SECRET": "secret",
                }
            )


class ReadmeSupabaseAuthFoundationTest(unittest.TestCase):
    def test_readme_documents_supabase_auth_foundation(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Supabase", content)
        self.assertIn(".env.example", content)
        self.assertIn("SUPABASE_URL", content)
        self.assertIn("auth.users", content)
        self.assertIn("JWT", content)
        self.assertIn("without querying the database", content)


if __name__ == "__main__":
    unittest.main()
