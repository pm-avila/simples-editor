import pathlib
import unittest

from backend.app import create_app


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


class HealthEndpointContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = create_app().test_client()

    def test_get_api_health_returns_ok_status(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_get_api_health_is_public(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.get_json())

    def test_get_api_health_reports_backend_service_name(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.get_json()["service"], "backend")


if __name__ == "__main__":
    unittest.main()
