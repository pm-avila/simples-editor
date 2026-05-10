"""
Tests for docker-compose.yml foundation contract (Tasks 1 & 2, Issue #3).

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v
"""

import os
import re
import unittest
import yaml

COMPOSE_FILE = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")
ENV_EXAMPLE_FILE = os.path.join(os.path.dirname(__file__), "..", ".env.example")
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
REQUIRED_SERVICES = {"nginx", "frontend", "backend"}
REQUIRED_VARIABLES = {
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_JWT_SECRET",
    "COMPILE_TIMEOUT",
    "EXECUTION_TIMEOUT",
    "SANDBOX_IMAGE",
}


class ComposeFoundationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(COMPOSE_FILE, "r") as f:
            cls.compose = yaml.safe_load(f)

    def test_compose_file_exists(self):
        self.assertTrue(
            os.path.isfile(COMPOSE_FILE),
            "docker-compose.yml must exist at repo root",
        )

    def test_compose_has_services_section(self):
        self.assertIn(
            "services", self.compose, "compose must have a 'services' top-level key"
        )

    def test_required_services_exist(self):
        defined = set(self.compose.get("services", {}).keys())
        missing = REQUIRED_SERVICES - defined
        self.assertFalse(missing, f"Missing services in compose: {missing}")

    def _collect_env_keys(self, service_def):
        """Return all environment variable names declared in a service definition."""
        env = service_def.get("environment", {})
        if isinstance(env, list):
            return {item.split("=")[0] for item in env}
        if isinstance(env, dict):
            return set(env.keys())
        return set()

    def test_required_variables_declared_in_backend(self):
        backend = self.compose.get("services", {}).get("backend", {})
        declared = self._collect_env_keys(backend)
        missing = REQUIRED_VARIABLES - declared
        self.assertFalse(
            missing,
            f"backend service is missing required environment variables: {missing}",
        )

    # Task 2: frontend and backend must declare build contexts
    def test_frontend_and_backend_use_build_contexts(self):
        """Task 2: frontend and backend must use local build contexts, not plain images."""
        services = self.compose.get("services", {})
        for name, expected_ctx in (("frontend", "./frontend"), ("backend", "./backend")):
            svc = services.get(name, {})
            build = svc.get("build")
            self.assertIsNotNone(
                build,
                f"Service '{name}' must declare a 'build' key with context '{expected_ctx}'.",
            )
            ctx = build if isinstance(build, str) else build.get("context", "")
            self.assertEqual(
                ctx,
                expected_ctx,
                f"Service '{name}' build context must be '{expected_ctx}', got '{ctx}'.",
            )

    # Task 2: nginx must declare depends_on frontend and backend
    def test_nginx_depends_on_frontend_and_backend(self):
        """nginx must declare depends_on for both frontend and backend."""
        nginx = self.compose.get("services", {}).get("nginx", {})
        depends_on = nginx.get("depends_on", [])
        if isinstance(depends_on, dict):
            depends_on = list(depends_on.keys())
        self.assertIn("frontend", depends_on, "nginx depends_on must include 'frontend'")
        self.assertIn("backend", depends_on, "nginx depends_on must include 'backend'")

    # Task 2: nginx must mount default.conf
    def test_nginx_mounts_default_conf(self):
        """nginx service must volume-mount nginx/default.conf."""
        nginx = self.compose.get("services", {}).get("nginx", {})
        volumes = nginx.get("volumes", [])
        self.assertTrue(
            any("default.conf" in str(v) for v in volumes),
            "nginx service must mount nginx/default.conf via volumes.",
        )

    # Task 2: frontend must be addressed on port 8080
    def test_compose_frontend_routes_on_8080(self):
        """frontend service must expose or map port 8080."""
        frontend = self.compose.get("services", {}).get("frontend", {})
        ports = frontend.get("ports", [])
        self.assertTrue(
            any("8080" in str(p) for p in ports),
            "frontend service must expose port 8080.",
        )

    # Task 2: backend must be addressed on port 5000
    def test_compose_backend_routes_on_5000(self):
        """backend service must expose or map port 5000."""
        backend = self.compose.get("services", {}).get("backend", {})
        ports = backend.get("ports", [])
        self.assertTrue(
            any("5000" in str(p) for p in ports),
            "backend service must expose port 5000.",
        )

    # Finding 2: env var refs must carry safe :-defaults
    def test_env_mappings_have_safe_defaults(self):
        """All ${VAR} refs in compose must use ${VAR:-default} so compose works without a .env file."""
        with open(COMPOSE_FILE, "r") as f:
            raw = f.read()
        bare_refs = re.findall(r"\$\{[A-Z_]+\}", raw)
        self.assertFalse(
            bare_refs,
            f"docker-compose.yml has env refs without ':-' defaults: {bare_refs}. "
            "Use ${VAR:-default} syntax instead.",
        )


# Task 2: service skeleton files must exist
class ServiceSkeletonFilesTest(unittest.TestCase):

    def _path(self, *parts):
        return os.path.join(REPO_ROOT, *parts)

    def test_frontend_dockerfile_exists(self):
        self.assertTrue(
            os.path.isfile(self._path("frontend", "Dockerfile")),
            "frontend/Dockerfile must exist",
        )

    def test_frontend_index_html_exists(self):
        self.assertTrue(
            os.path.isfile(self._path("frontend", "index.html")),
            "frontend/index.html must exist",
        )

    def test_frontend_server_py_exists(self):
        self.assertTrue(
            os.path.isfile(self._path("frontend", "server.py")),
            "frontend/server.py must exist",
        )

    def test_backend_dockerfile_exists(self):
        self.assertTrue(
            os.path.isfile(self._path("backend", "Dockerfile")),
            "backend/Dockerfile must exist",
        )

    def test_backend_requirements_txt_exists(self):
        self.assertTrue(
            os.path.isfile(self._path("backend", "requirements.txt")),
            "backend/requirements.txt must exist",
        )

    def test_backend_app_py_exists(self):
        self.assertTrue(
            os.path.isfile(self._path("backend", "app.py")),
            "backend/app.py must exist",
        )

    def test_nginx_default_conf_exists(self):
        self.assertTrue(
            os.path.isfile(self._path("nginx", "default.conf")),
            "nginx/default.conf must exist",
        )


# Finding 3: .env.example must exist and expose every required variable
class EnvExampleTest(unittest.TestCase):

    def test_env_example_exists(self):
        self.assertTrue(
            os.path.isfile(ENV_EXAMPLE_FILE),
            ".env.example must exist at repo root",
        )

    def test_env_example_contains_required_keys(self):
        with open(ENV_EXAMPLE_FILE, "r") as f:
            lines = f.readlines()
        keys = set()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                keys.add(line.split("=")[0])
        missing = REQUIRED_VARIABLES - keys
        self.assertFalse(
            missing,
            f".env.example is missing required keys: {missing}",
        )


if __name__ == "__main__":
    unittest.main()
