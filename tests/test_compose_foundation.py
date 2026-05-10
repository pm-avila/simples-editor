"""
Tests for docker-compose.yml foundation contract (Task 1, Issue #3).

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v
"""

import os
import unittest
import yaml

COMPOSE_FILE = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")
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

    def test_services_do_not_use_local_build_contexts(self):
        """Task 1 scope: compose must be self-contained; local build contexts belong to later tasks."""
        services = self.compose.get("services", {})
        for name, svc in services.items():
            build = svc.get("build")
            if build is not None:
                ctx = build if isinstance(build, str) else build.get("context", "")
                self.assertFalse(
                    ctx.startswith("./frontend") or ctx.startswith("./backend"),
                    f"Service '{name}' must not reference local build context '{ctx}' in Task 1; "
                    "use a placeholder image instead.",
                )


if __name__ == "__main__":
    unittest.main()
