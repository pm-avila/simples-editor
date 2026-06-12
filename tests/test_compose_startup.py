"""
Tests for compose startup scaffold — Task 1, Issue #4.

Verifies that all required files exist and carry the structural
contracts defined in the task spec:

  - docker-compose.yml  : nginx on 80:80, frontend/backend build contexts,
                          expose 8080/5000, env :-defaults on backend,
                          nginx volume mount and depends_on
  - .env.example        : six required env keys
  - frontend/Dockerfile
  - frontend/index.html
  - frontend/server.py  : ThreadingHTTPServer on port 8080
  - backend/Dockerfile
  - backend/requirements.txt
  - backend/app.py      : routes at / and /health
  - nginx/default.conf  : root → frontend:8080, /api/ → backend:5000/

Run with:
    python3 -m unittest tests/test_compose_startup.py -v
"""

import ast
import os
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

COMPOSE_FILE = os.path.join(REPO_ROOT, "docker-compose.yml")
ENV_EXAMPLE = os.path.join(REPO_ROOT, ".env.example")
NGINX_CONF = os.path.join(REPO_ROOT, "nginx", "default.conf")
FRONTEND_DOCKERFILE = os.path.join(REPO_ROOT, "frontend", "Dockerfile")
FRONTEND_INDEX = os.path.join(REPO_ROOT, "frontend", "index.html")
FRONTEND_SERVER = os.path.join(REPO_ROOT, "frontend", "server.py")
BACKEND_DOCKERFILE = os.path.join(REPO_ROOT, "backend", "Dockerfile")
BACKEND_REQUIREMENTS = os.path.join(REPO_ROOT, "backend", "requirements.txt")
BACKEND_APP = os.path.join(REPO_ROOT, "backend", "app.py")
README_FILE = os.path.join(REPO_ROOT, "README.md")

REQUIRED_ENV_KEYS = {
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "COMPILE_TIMEOUT",
    "EXECUTION_TIMEOUT",
    "SANDBOX_IMAGE",
}


def _service_block(raw: str, service_name: str) -> str:
    """Return the indented text block owned by *service_name* in a compose YAML string."""
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

        if stripped and not stripped.startswith("#") and indent <= header_indent:
            break
        block.append(line)

    return "\n".join(block)


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

class FileExistenceTest(unittest.TestCase):

    def test_docker_compose_yml_exists(self):
        self.assertTrue(os.path.isfile(COMPOSE_FILE), "docker-compose.yml must exist at repo root")

    def test_env_example_exists(self):
        self.assertTrue(os.path.isfile(ENV_EXAMPLE), ".env.example must exist at repo root")

    def test_frontend_dockerfile_exists(self):
        self.assertTrue(os.path.isfile(FRONTEND_DOCKERFILE), "frontend/Dockerfile must exist")

    def test_frontend_index_html_exists(self):
        self.assertTrue(os.path.isfile(FRONTEND_INDEX), "frontend/index.html must exist")

    def test_frontend_server_py_exists(self):
        self.assertTrue(os.path.isfile(FRONTEND_SERVER), "frontend/server.py must exist")

    def test_backend_dockerfile_exists(self):
        self.assertTrue(os.path.isfile(BACKEND_DOCKERFILE), "backend/Dockerfile must exist")

    def test_backend_requirements_txt_exists(self):
        self.assertTrue(os.path.isfile(BACKEND_REQUIREMENTS), "backend/requirements.txt must exist")

    def test_backend_app_py_exists(self):
        self.assertTrue(os.path.isfile(BACKEND_APP), "backend/app.py must exist")

    def test_nginx_default_conf_exists(self):
        self.assertTrue(os.path.isfile(NGINX_CONF), "nginx/default.conf must exist")


# ---------------------------------------------------------------------------
# docker-compose.yml contracts
# ---------------------------------------------------------------------------

class ComposeStructureTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(COMPOSE_FILE) as f:
            cls.raw = f.read()

    def test_nginx_exposes_port_80_on_host(self):
        nginx = _service_block(self.raw, "nginx")
        self.assertRegex(nginx, r"[\"']?80:80[\"']?", "nginx must map host port 80 to container 80")

    def test_frontend_build_context_is_frontend_dir(self):
        block = _service_block(self.raw, "frontend")
        self.assertIn("build", block, "frontend must have a build section")
        self.assertRegex(block, r"context:\s*\./frontend", "frontend build context must be ./frontend")

    def test_backend_build_context_is_backend_dir(self):
        block = _service_block(self.raw, "backend")
        self.assertIn("build", block, "backend must have a build section")
        self.assertRegex(block, r"context:\s*\./backend", "backend build context must be ./backend")

    def test_frontend_exposes_8080(self):
        block = _service_block(self.raw, "frontend")
        self.assertIn("8080", block, "frontend must expose port 8080")

    def test_backend_exposes_5000(self):
        block = _service_block(self.raw, "backend")
        self.assertIn("5000", block, "backend must expose port 5000")

    def test_backend_env_vars_have_safe_defaults(self):
        block = _service_block(self.raw, "backend")
        bare_refs = re.findall(r"\$\{[A-Z_]+\}", block)
        self.assertFalse(
            bare_refs,
            f"backend env vars must use ${{VAR:-default}} syntax; bare refs found: {bare_refs}",
        )

    def test_backend_environment_block_exists(self):
        block = _service_block(self.raw, "backend")
        self.assertRegex(
            block,
            r"\benvironment\b",
            "backend service must declare an 'environment' block",
        )

    def test_backend_environment_has_all_required_keys(self):
        block = _service_block(self.raw, "backend")
        missing = [k for k in REQUIRED_ENV_KEYS if k not in block]
        self.assertFalse(
            missing,
            f"backend environment block is missing required keys: {missing}",
        )

    def test_backend_environment_keys_use_safe_defaults(self):
        block = _service_block(self.raw, "backend")
        bad = [
            k for k in REQUIRED_ENV_KEYS
            if not re.search(rf"{re.escape(k)}:\s*\$\{{{re.escape(k)}:-[^}}]+\}}", block)
        ]
        self.assertFalse(
            bad,
            f"backend env keys must use ${{KEY:-default}} syntax; non-compliant keys: {bad}",
        )

    def test_nginx_mounts_default_conf(self):
        block = _service_block(self.raw, "nginx")
        self.assertIn("default.conf", block, "nginx must volume-mount nginx/default.conf")

    def test_nginx_depends_on_frontend_and_backend(self):
        block = _service_block(self.raw, "nginx")
        self.assertIn("depends_on", block, "nginx must declare depends_on")
        for svc in ("frontend", "backend"):
            self.assertIn(svc, block, f"nginx depends_on must list '{svc}'")

    def test_frontend_and_backend_have_no_host_port_binding(self):
        for name in ("frontend", "backend"):
            block = _service_block(self.raw, name)
            host_bindings = re.findall(r"-\s+[\"']?\d+:\d+[\"']?", block)
            self.assertFalse(
                host_bindings,
                f"{name} must not bind host ports (all traffic through nginx): {host_bindings}",
            )


# ---------------------------------------------------------------------------
# .env.example contracts
# ---------------------------------------------------------------------------

class EnvExampleTest(unittest.TestCase):

    def test_env_example_has_required_keys(self):
        with open(ENV_EXAMPLE) as f:
            keys = {
                line.split("=")[0].strip()
                for line in f
                if line.strip() and not line.startswith("#") and "=" in line
            }
        missing = REQUIRED_ENV_KEYS - keys
        self.assertFalse(missing, f".env.example missing required keys: {missing}")


# ---------------------------------------------------------------------------
# frontend/server.py contracts
# ---------------------------------------------------------------------------

class FrontendServerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(FRONTEND_SERVER) as f:
            cls.src = f.read()

    def test_uses_threading_http_server(self):
        self.assertIn("ThreadingHTTPServer", self.src, "frontend/server.py must use ThreadingHTTPServer")

    def test_listens_on_port_8080(self):
        self.assertIn("8080", self.src, "frontend/server.py must listen on port 8080")


# ---------------------------------------------------------------------------
# backend/app.py contracts
# ---------------------------------------------------------------------------

class BackendAppTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(BACKEND_APP) as f:
            cls.src = f.read()

    def test_has_root_route(self):
        self.assertIn('@app.route("/")', self.src, "backend/app.py must define a route at '/'")

    def test_has_health_route(self):
        self.assertIn('/health', self.src, "backend/app.py must define a /health route")


# ---------------------------------------------------------------------------
# backend/app.py route-response contracts
# ---------------------------------------------------------------------------

class BackendAppRouteResponseTest(unittest.TestCase):
    """Verify / and /health return jsonify({"status": "ok"}) without importing Flask."""

    @classmethod
    def setUpClass(cls):
        with open(BACKEND_APP) as f:
            cls.tree = ast.parse(f.read(), filename=BACKEND_APP)

    def _assert_route_returns_status_ok(self, function_name):
        function = next(
            (
                node for node in self.tree.body
                if isinstance(node, ast.FunctionDef) and node.name == function_name
            ),
            None,
        )
        self.assertIsNotNone(function, f"{function_name} route handler must exist")
        self.assertTrue(function.body, f"{function_name} must have a body")
        return_stmt = next(
            (node for node in ast.walk(function) if isinstance(node, ast.Return)),
            None,
        )
        self.assertIsInstance(return_stmt, ast.Return, f"{function_name} must return a response")
        call = return_stmt.value
        self.assertIsInstance(call, ast.Call, f"{function_name} must return a call expression")
        self.assertIsInstance(call.func, ast.Name, f"{function_name} must call jsonify")
        self.assertEqual(call.func.id, "jsonify", f"{function_name} must call jsonify")
        self.assertEqual(len(call.args), 1, f"{function_name} must pass exactly one payload to jsonify")
        payload = call.args[0]
        self.assertIsInstance(payload, ast.Dict, f"{function_name} must return a dict payload")
        keys = [key.value for key in payload.keys if isinstance(key, ast.Constant)]
        values = [value.value for value in payload.values if isinstance(value, ast.Constant)]
        self.assertEqual(keys, ["status"], f"{function_name} must return only the status key")
        self.assertEqual(values, ["ok"], f"{function_name} must return status ok")

    def test_root_route_returns_status_ok(self):
        self._assert_route_returns_status_ok("index")

    def test_health_route_returns_status_ok(self):
        self._assert_route_returns_status_ok("health")


class BackendAppRouteResponseRegressionTest(unittest.TestCase):
    def test_route_contract_ignores_docstring_before_return(self):
        checker = BackendAppRouteResponseTest()
        checker.tree = ast.parse(
            """
from flask import jsonify

def index():
    \"\"\"Docs.\"\"\"
    return jsonify({"status": "ok"})
"""
        )

        checker._assert_route_returns_status_ok("index")

    def test_missing_route_handler_fails_with_assertion(self):
        checker = BackendAppRouteResponseTest()
        checker.tree = ast.parse(
            """
from flask import jsonify

def index():
    return jsonify({"status": "ok"})
"""
        )

        with self.assertRaises(AssertionError):
            checker._assert_route_returns_status_ok("health")


# ---------------------------------------------------------------------------
# nginx/default.conf contracts
# ---------------------------------------------------------------------------

class NginxConfTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(NGINX_CONF) as f:
            cls.src = f.read()

    def test_root_proxies_to_frontend(self):
        self.assertRegex(
            self.src,
            r"proxy_pass\s+http://frontend:8080",
            "nginx must proxy root location to http://frontend:8080",
        )

    def test_api_location_proxies_to_backend_root(self):
        self.assertIn(
            "proxy_pass http://backend:5000/",
            self.src,
            "nginx /api/ location must proxy_pass to http://backend:5000/ (trailing slash strips prefix)",
        )


# ---------------------------------------------------------------------------
# Task 2: Operational startup topology contract
# ---------------------------------------------------------------------------

class NginxEntryPointContractTest(unittest.TestCase):
    """Task 2 — nginx must be the single host entry point in docker-compose.yml."""

    @classmethod
    def setUpClass(cls):
        with open(COMPOSE_FILE) as f:
            cls.raw = f.read()

    def _all_service_names(self):
        """Return all top-level service names from the compose file."""
        in_services = False
        names = []
        for line in self.raw.splitlines():
            if re.match(r"^services\s*:", line):
                in_services = True
                continue
            if in_services:
                if re.match(r"^[^\s#][^:]*\s*:", line):
                    break
                m = re.match(r"^  (\w[\w-]*)\s*:", line)
                if m:
                    names.append(m.group(1))
        return names

    def test_nginx_is_the_only_service_with_host_port_bindings(self):
        """Only nginx may bind host ports; every other service must use expose."""
        for name in self._all_service_names():
            block = _service_block(self.raw, name)
            host_bindings = re.findall(r"-\s+[\"']?\d+:\d+[\"']?", block)
            if name == "nginx":
                self.assertTrue(
                    host_bindings,
                    "nginx must have at least one host port binding (80:80)",
                )
            else:
                self.assertFalse(
                    host_bindings,
                    f"service '{name}' must not bind host ports — all traffic must flow through nginx: {host_bindings}",
                )


class NginxEntryPointContractRegressionTest(unittest.TestCase):
    def test_all_service_names_stops_at_next_top_level_section(self):
        checker = NginxEntryPointContractTest()
        checker.raw = """
services:
  nginx:
    image: nginx:alpine
  frontend:
    image: python:3.12-alpine

volumes:
  cache:
"""

        self.assertEqual(checker._all_service_names(), ["nginx", "frontend"])

    def test_nginx_conf_listen_directive_is_port_80(self):
        with open(NGINX_CONF) as f:
            conf = f.read()
        self.assertRegex(
            conf,
            r"\blisten\s+80\s*;",
            "nginx/default.conf must declare 'listen 80;'",
        )


class NginxRoutingContractTest(unittest.TestCase):
    """Task 2 — nginx location blocks must proxy to the correct upstreams."""

    @classmethod
    def setUpClass(cls):
        with open(NGINX_CONF) as f:
            cls.src = f.read()

    def test_root_location_block_proxies_to_frontend(self):
        self.assertRegex(
            self.src,
            r"location\s+/\s*\{[^}]*proxy_pass\s+http://frontend:8080",
            "nginx 'location /' block must proxy_pass to http://frontend:8080",
        )

    def test_api_location_block_proxies_to_backend_with_trailing_slash(self):
        self.assertRegex(
            self.src,
            r"location\s+/api/\s*\{[^}]*proxy_pass\s+http://backend:5000/",
            "nginx 'location /api/' block must proxy_pass to http://backend:5000/ (trailing slash strips /api/ prefix)",
        )


class BackendRootRouteContractTest(unittest.TestCase):
    """Task 2 — backend '/' route must serve {"status": "ok"} (static AST verification).

    Enforces the Task 2 contract without importing Flask or executing backend/app.py,
    so the test is reproducible in any environment that has Python 3 stdlib only.
    """

    @classmethod
    def setUpClass(cls):
        with open(BACKEND_APP) as f:
            cls.tree = ast.parse(f.read(), filename=BACKEND_APP)

    def _find_route_handler(self, path: str):
        """Return the FunctionDef whose @app.route(path) decorator matches *path*, or None."""
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "route"
                    and decorator.args
                    and isinstance(decorator.args[0], ast.Constant)
                    and decorator.args[0].value == path
                ):
                    return node
        return None

    def test_root_route_handler_exists(self):
        handler = self._find_route_handler("/")
        self.assertIsNotNone(
            handler,
            "backend/app.py must define a function decorated with @app.route('/')",
        )

    def test_root_route_returns_status_ok(self):
        handler = self._find_route_handler("/")
        self.assertIsNotNone(handler, "backend/app.py must define @app.route('/')")
        return_stmts = [n for n in ast.walk(handler) if isinstance(n, ast.Return)]
        self.assertTrue(return_stmts, "route '/' handler must contain a return statement")
        ret = return_stmts[0]
        self.assertIsInstance(ret.value, ast.Call, "route '/' must return a call expression")
        call = ret.value
        self.assertIsInstance(call.func, ast.Name, "route '/' must call a bare function (jsonify)")
        self.assertEqual(call.func.id, "jsonify", "route '/' must call jsonify")
        self.assertEqual(len(call.args), 1, "jsonify must receive exactly one positional argument")
        payload = call.args[0]
        self.assertIsInstance(payload, ast.Dict, "jsonify argument must be a dict literal")
        keys = [k.value for k in payload.keys if isinstance(k, ast.Constant)]
        values = [v.value for v in payload.values if isinstance(v, ast.Constant)]
        self.assertEqual(keys, ["status"], "route '/' payload must have only the key 'status'")
        self.assertEqual(values, ["ok"], "route '/' payload must carry the value 'ok'")


class ReadmeStartupFlowTest(unittest.TestCase):
    """Task 3 — README must describe the real local docker compose startup flow."""

    @classmethod
    def setUpClass(cls):
        with open(README_FILE) as f:
            cls.src = f.read()

    def test_readme_documents_real_local_startup_flow(self):
        for required in (
            "docker compose up --build",
            "http://localhost",
            ".env.example",
            "nginx",
        ):
            self.assertIn(
                required,
                self.src,
                f"README.md must mention '{required}' in the local startup instructions",
            )


if __name__ == "__main__":
    unittest.main()
