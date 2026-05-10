"""
Tests for docker-compose.yml foundation contract (Task 1, Issue #3).
"""

import os
import pytest
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


@pytest.fixture(scope="module")
def compose():
    with open(COMPOSE_FILE, "r") as f:
        return yaml.safe_load(f)


def test_compose_file_exists():
    assert os.path.isfile(COMPOSE_FILE), "docker-compose.yml must exist at repo root"


def test_compose_has_services_section(compose):
    assert "services" in compose, "compose must have a 'services' top-level key"


def test_required_services_exist(compose):
    defined = set(compose.get("services", {}).keys())
    missing = REQUIRED_SERVICES - defined
    assert not missing, f"Missing services in compose: {missing}"


def _collect_env_keys(service_def: dict) -> set:
    """Return all environment variable names declared in a service definition."""
    env = service_def.get("environment", {})
    if isinstance(env, list):
        return {item.split("=")[0] for item in env}
    if isinstance(env, dict):
        return set(env.keys())
    return set()


def test_required_variables_declared_in_backend(compose):
    backend = compose.get("services", {}).get("backend", {})
    declared = _collect_env_keys(backend)
    missing = REQUIRED_VARIABLES - declared
    assert not missing, (
        f"backend service is missing required environment variables: {missing}"
    )
