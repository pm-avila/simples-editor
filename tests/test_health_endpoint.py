import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class HealthEndpointFoundationTest(unittest.TestCase):
    def test_required_backend_files_exist(self):
        required = [
            ROOT / "backend" / "__init__.py",
            ROOT / "backend" / "requirements.txt",
            ROOT / "tests" / "test_health_endpoint.py",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_backend_requirements_include_flask(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("flask==", content.lower())


if __name__ == "__main__":
    unittest.main()
