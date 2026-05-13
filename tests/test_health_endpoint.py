import pathlib
import importlib.util
import sys
import unittest
from unittest.mock import patch


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


class HealthEndpointCompatibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = _load_create_app()().test_client()

    def test_legacy_compose_routes_remain_available(self):
        for path in ("/", "/health"):
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), {"status": "ok"})


class HealthEndpointWithoutSockDependencyTest(unittest.TestCase):
    def test_backend_app_imports_without_flask_sock_and_http_routes_work(self):
        module_path = ROOT / "backend" / "app.py"
        spec = importlib.util.spec_from_file_location("backend.app_without_sock", module_path)
        module = importlib.util.module_from_spec(spec)
        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "flask_sock":
                raise ModuleNotFoundError("No module named 'flask_sock'")
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=fake_import):
            spec.loader.exec_module(module)

        app = module.create_app()
        rules = {rule.rule for rule in app.url_map.iter_rules()}
        self.assertIn("/", rules)
        self.assertIn("/health", rules)
        self.assertIn("/api/health", rules)
        self.assertIn("/api/compile", rules)
        self.assertNotIn("/ws/run", rules)

        response = app.test_client().get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")


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
