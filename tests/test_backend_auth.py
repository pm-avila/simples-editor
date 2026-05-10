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


from dataclasses import dataclass


@dataclass
class FakeRequest:
    headers: dict
    user_id: str | None = None


class BackendVerifyJwtDecoratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = ROOT / "backend" / "auth.py"
        spec = importlib.util.spec_from_file_location("backend.auth", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_verify_jwt_rejects_missing_authorization_header(self):
        request = FakeRequest(headers={})

        @self.module.verify_jwt("secret")
        def handler(current_request):
            return current_request.user_id

        with self.assertRaises(self.module.AuthError):
            handler(request)

    def test_verify_jwt_rejects_empty_bearer_token(self):
        request = FakeRequest(headers={"Authorization": "Bearer "})

        @self.module.verify_jwt("secret")
        def handler(current_request):
            return current_request.user_id

        with self.assertRaisesRegex(self.module.AuthError, "missing bearer token"):
            handler(request)

    def test_verify_jwt_injects_user_id_from_sub_claim(self):
        token = jwt.encode({"sub": "user-123"}, "secret", algorithm="HS256")
        request = FakeRequest(headers={"Authorization": f"Bearer {token}"})

        @self.module.verify_jwt("secret")
        def handler(current_request):
            return current_request.user_id

        self.assertEqual(handler(request), "user-123")


class BackendJwtReadmeTest(unittest.TestCase):
    def test_readme_documents_backend_jwt_validation(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Backend JWT validation", content)
        self.assertIn("verify_jwt", content)
        self.assertIn("SUPABASE_JWT_SECRET", content)
        self.assertIn("sub", content)
        self.assertIn("user_id", content)
        self.assertIn("JWT", content)
        self.assertIn("without querying the database", content)


if __name__ == "__main__":
    unittest.main()
