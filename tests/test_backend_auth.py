import pathlib
import unittest


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


if __name__ == "__main__":
    unittest.main()
