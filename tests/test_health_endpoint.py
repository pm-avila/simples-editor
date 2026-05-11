import pathlib
import importlib.util
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND_APP_IMPORTED_AT_MODULE_LOAD = "backend.app" in sys.modules


def _load_create_app():
    module_path = ROOT / "backend" / "app.py"
    spec = importlib.util.spec_from_file_location("backend.app", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.create_app


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

    def test_backend_app_is_not_imported_at_module_load(self):
        self.assertFalse(
            BACKEND_APP_IMPORTED_AT_MODULE_LOAD,
            "backend.app should load lazily in setUpClass",
        )


class HealthEndpointContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = _load_create_app()().test_client()

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


class HealthEndpointReadmeTest(unittest.TestCase):
    def test_readme_documents_public_health_check(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("/api/health", content)
        self.assertIn("GET", content)
        self.assertIn("status", content)
        self.assertIn("ok", content)
        self.assertIn("without JWT", content)


if __name__ == "__main__":
    unittest.main()
