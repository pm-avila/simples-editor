import pathlib
import unittest
import importlib.util

import jwt


ROOT = pathlib.Path(__file__).resolve().parents[1]


class BackendAuthFoundationTest(unittest.TestCase):
    def test_backend_auth_files_exist(self):
        required = [
            ROOT / "backend" / "__init__.py",
            ROOT / "backend" / "requirements.txt",
            ROOT / "tests" / "test_backend_auth.py",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_backend_requirements_include_pyjwt(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("PyJWT==", content)


class BackendJwtCoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = ROOT / "backend" / "auth.py"
        spec = importlib.util.spec_from_file_location("backend.auth", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_decode_supabase_jwt_accepts_valid_token(self):
        token = jwt.encode({"sub": "user-123"}, "secret", algorithm="HS256")
        claims = self.module.decode_supabase_jwt(token, "secret")
        self.assertEqual(claims["sub"], "user-123")

    def test_decode_supabase_jwt_rejects_invalid_token(self):
        with self.assertRaisesRegex(self.module.AuthError, "invalid token"):
            self.module.decode_supabase_jwt("not-a-jwt", "secret")

    def test_extract_user_id_returns_sub(self):
        self.assertEqual(self.module.extract_user_id({"sub": "user-123"}), "user-123")

    def test_extract_user_id_rejects_missing_sub(self):
        with self.assertRaises(self.module.AuthError):
            self.module.extract_user_id({})


if __name__ == "__main__":
    unittest.main()
