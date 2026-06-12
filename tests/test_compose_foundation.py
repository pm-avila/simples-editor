"""
Tests for docker-compose.yml foundation contract (Tasks 1 & 2, Issue #3).

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compose_foundation.py -v
"""

import os
import re
import unittest

COMPOSE_FILE = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")
ENV_EXAMPLE_FILE = os.path.join(os.path.dirname(__file__), "..", ".env.example")
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
NGINX_CONF_FILE = os.path.join(REPO_ROOT, "nginx", "default.conf")
BACKEND_APP_FILE = os.path.join(REPO_ROOT, "backend", "app.py")
FRONTEND_SERVER_FILE = os.path.join(REPO_ROOT, "frontend", "server.py")
REQUIRED_SERVICES = {"nginx", "frontend", "backend"}
REQUIRED_VARIABLES = {
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "COMPILE_TIMEOUT",
    "EXECUTION_TIMEOUT",
    "SANDBOX_IMAGE",
}


def _extract_service_block(raw, service_name):
    """Return the indented text block owned by *service_name* in a docker-compose YAML string.

    Uses indentation-based line parsing so no third-party library is required.
    The block starts after the ``service_name:`` header line and ends when a
    non-blank, non-comment line at the same or lesser indentation level is seen.
    """
    lines = raw.splitlines()
    in_services = False
    in_target = False
    header_indent = None
    block = []

    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if not in_services:
            if re.match(r"^services\s*:", line):
                in_services = True
            continue

        if not in_target:
            if re.match(rf"^\s+{re.escape(service_name)}\s*:", line):
                in_target = True
                header_indent = indent
            continue

        # Collect lines until we exit the service's indented block.
        if stripped and not stripped.startswith("#") and indent <= header_indent:
            break
        block.append(line)

    return "\n".join(block)


class ComposeFoundationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(COMPOSE_FILE, "r") as f:
            cls.compose_raw = f.read()

    def test_compose_file_exists(self):
        self.assertTrue(
            os.path.isfile(COMPOSE_FILE),
            "docker-compose.yml must exist at repo root",
        )

    def test_compose_has_services_section(self):
        self.assertRegex(
            self.compose_raw,
            r"(?m)^services\s*:",
            "compose must have a 'services' top-level key",
        )

    def test_required_services_exist(self):
        missing = set()
        for svc in REQUIRED_SERVICES:
            block = _extract_service_block(self.compose_raw, svc)
            if not block and not re.search(
                rf"(?m)^\s+{re.escape(svc)}\s*:", self.compose_raw
            ):
                missing.add(svc)
        self.assertFalse(missing, f"Missing services in compose: {missing}")

    def test_required_variables_declared_in_backend(self):
        backend_block = _extract_service_block(self.compose_raw, "backend")
        missing = {var for var in REQUIRED_VARIABLES if var not in backend_block}
        self.assertFalse(
            missing,
            f"backend service is missing required environment variables: {missing}",
        )

    # Task 2: frontend and backend must declare build contexts
    def test_frontend_and_backend_use_build_contexts(self):
        """Task 2: frontend and backend must use local build contexts, not plain images."""
        for name, expected_ctx in (("frontend", "./frontend"), ("backend", "./backend")):
            block = _extract_service_block(self.compose_raw, name)
            self.assertIn(
                "build",
                block,
                f"Service '{name}' must declare a 'build' key with context '{expected_ctx}'.",
            )
            self.assertRegex(
                block,
                rf"context:\s*{re.escape(expected_ctx)}",
                f"Service '{name}' build context must be '{expected_ctx}'.",
            )

    # Task 2: nginx must declare depends_on frontend and backend
    def test_nginx_depends_on_frontend_and_backend(self):
        """nginx must declare depends_on for both frontend and backend."""
        nginx_block = _extract_service_block(self.compose_raw, "nginx")
        self.assertIn("depends_on", nginx_block, "nginx must declare depends_on")
        for svc in ("frontend", "backend"):
            found = f"- {svc}" in nginx_block or bool(
                re.search(rf"(?m)^\s+{re.escape(svc)}\s*:", nginx_block)
            )
            self.assertTrue(found, f"nginx depends_on must include '{svc}'")

    # Task 2: nginx must mount default.conf
    def test_nginx_mounts_default_conf(self):
        """nginx service must volume-mount nginx/default.conf."""
        nginx_block = _extract_service_block(self.compose_raw, "nginx")
        self.assertIn(
            "default.conf",
            nginx_block,
            "nginx service must mount nginx/default.conf via volumes.",
        )

    # Finding 2: nginx is the sole host entry point — frontend/backend must NOT bind host ports
    def test_frontend_has_no_host_port_binding(self):
        """frontend must not bind host ports; all external traffic flows through nginx."""
        frontend_block = _extract_service_block(self.compose_raw, "frontend")
        # List-item port bindings look like: - "HOST:CONTAINER" or - HOST:CONTAINER
        host_bindings = re.findall(r"-\s+[\"']?\d+:\d+[\"']?", frontend_block)
        self.assertFalse(
            host_bindings,
            f"frontend must not bind host ports. Remove {host_bindings} from its 'ports' list.",
        )

    def test_backend_has_no_host_port_binding(self):
        """backend must not bind host ports; all external traffic flows through nginx."""
        backend_block = _extract_service_block(self.compose_raw, "backend")
        host_bindings = re.findall(r"-\s+[\"']?\d+:\d+[\"']?", backend_block)
        self.assertFalse(
            host_bindings,
            f"backend must not bind host ports. Remove {host_bindings} from its 'ports' list.",
        )

    def test_nginx_is_sole_host_entry_point_on_port_80(self):
        """nginx must be the only service with a host-bound port (port 80)."""
        nginx_block = _extract_service_block(self.compose_raw, "nginx")
        self.assertRegex(
            nginx_block,
            r"[\"']?80:\d+[\"']?",
            "nginx must expose port 80 to the host as the sole entry point.",
        )

    # Finding 1: nginx /api/ location must strip the prefix when forwarding to backend
    def test_nginx_api_location_proxies_to_backend_root(self):
        """nginx /api/ location must proxy_pass to http://backend:5000/ (trailing slash
        causes nginx to strip the /api/ prefix before forwarding to the backend)."""
        with open(NGINX_CONF_FILE, "r") as f:
            content = f.read()
        self.assertIn(
            "proxy_pass http://backend:5000/",
            content,
            "nginx /api/ location must use 'proxy_pass http://backend:5000/' "
            "(trailing slash strips the /api/ prefix).",
        )

    # Finding 1: backend must respond at its root path (GET /)
    def test_backend_serves_root_path(self):
        """backend/app.py must define a route at '/' so nginx-forwarded /api/ requests land correctly."""
        with open(BACKEND_APP_FILE, "r") as f:
            content = f.read()
        self.assertIn(
            '@app.route("/")',
            content,
            "backend/app.py must define a route at '/' (nginx strips /api/ before forwarding).",
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

    # Finding 4: frontend/server.py must use ThreadingHTTPServer
    def test_frontend_server_uses_threading_http_server(self):
        """frontend/server.py must use ThreadingHTTPServer for concurrent request handling."""
        with open(FRONTEND_SERVER_FILE, "r") as f:
            content = f.read()
        self.assertIn(
            "ThreadingHTTPServer",
            content,
            "frontend/server.py must use ThreadingHTTPServer (not TCPServer).",
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


# Task 3: README must document the real compose scaffold
README_FILE = os.path.join(REPO_ROOT, "README.md")

README_REQUIRED_MENTIONS = [
    "docker-compose.yml",
    ".env.example",
    "nginx/default.conf",
    "frontend/",
    "backend/",
    "docker compose up --build",
    "nginx",
]


class ReadmeDocumentationTest(unittest.TestCase):
    """Task 3 (Issue #3): README must document the real compose scaffold."""

    @classmethod
    def setUpClass(cls):
        with open(README_FILE, "r") as f:
            cls.readme = f.read()

    def test_readme_mentions_docker_compose_yml(self):
        self.assertIn(
            "docker-compose.yml",
            self.readme,
            "README must mention docker-compose.yml",
        )

    def test_readme_mentions_env_example(self):
        self.assertIn(
            ".env.example",
            self.readme,
            "README must mention .env.example",
        )

    def test_readme_mentions_nginx_default_conf(self):
        self.assertIn(
            "nginx/default.conf",
            self.readme,
            "README must mention nginx/default.conf",
        )

    def test_readme_mentions_frontend_directory(self):
        self.assertIn(
            "frontend/",
            self.readme,
            "README must mention frontend/",
        )

    def test_readme_mentions_backend_directory(self):
        self.assertIn(
            "backend/",
            self.readme,
            "README must mention backend/",
        )

    def test_readme_mentions_docker_compose_up_build(self):
        self.assertIn(
            "docker compose up --build",
            self.readme,
            "README must include the real local dev command: docker compose up --build",
        )

    def test_readme_mentions_nginx_as_entry_point(self):
        """README must describe nginx as the single entry point."""
        content_lower = self.readme.lower()
        self.assertIn(
            "nginx",
            content_lower,
            "README must mention nginx as the entry point",
        )
        self.assertTrue(
            "entry point" in content_lower or "porta 80" in content_lower or "port 80" in content_lower,
            "README must describe nginx as the single/sole entry point on port 80",
        )


if __name__ == "__main__":
    unittest.main()
