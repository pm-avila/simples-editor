import pathlib
import unittest


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
        self.assertIn("SUPABASE_JWT_SECRET=", content)

    def test_supabase_config_enables_auth_for_local_project(self):
        content = (ROOT / "supabase" / "config.toml").read_text(encoding="utf-8")
        self.assertIn("project_id =", content)
        self.assertIn("[auth]", content)
        self.assertIn("site_url =", content)
        self.assertIn("enable_signup =", content)

    def test_backend_requirements_prepare_local_jwt_validation(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("PyJWT==", content)


if __name__ == "__main__":
    unittest.main()
