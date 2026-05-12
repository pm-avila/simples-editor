"""
Regression tests for backend/Dockerfile packaging contract.

The backend application uses `from backend.health import build_health_payload`,
which requires the entire `backend` package to be present at runtime — not just
app.py. This file asserts the two minimal Dockerfile invariants that prevent the
container-level ImportError:

  1. The Dockerfile copies the whole backend package into the image
     (not only app.py), so `backend/__init__.py` and siblings are available.
  2. The entrypoint runs Python in module mode (`python3 -m backend.app`) so
     the `backend` package is resolvable on sys.path.

Run with:
    python3 -m unittest tests/test_backend_dockerfile.py -v
"""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "backend" / "Dockerfile"


def _dockerfile_text():
    return DOCKERFILE.read_text(encoding="utf-8")


class BackendDockerfilePackagingTest(unittest.TestCase):
    """The Dockerfile must copy the whole backend package, not just app.py."""

    def test_dockerfile_copies_package_not_only_app_py(self):
        """COPY must include more than a single app.py so the package is present."""
        text = _dockerfile_text()
        # A bare `COPY app.py .` (or `COPY app.py /app/`) covers only one file.
        # Accept any COPY that is NOT exclusively `app.py`:
        #   COPY . .          — copies everything
        #   COPY . ./backend  — copies everything under a package sub-dir
        #   etc.
        bare_app_copy = re.compile(
            r"^\s*COPY\s+app\.py\s+\S*\s*$", re.MULTILINE
        )
        self.assertFalse(
            bare_app_copy.search(text),
            "Dockerfile must not copy only app.py; the full backend package "
            "(including __init__.py and health.py) must be included in the image.",
        )

    def test_dockerfile_copies_backend_package_contents(self):
        """COPY must bring in the full package (. or backend/ directory)."""
        text = _dockerfile_text()
        # Accept patterns like:
        #   COPY . .
        #   COPY . ./backend
        #   COPY . /app/backend/
        package_copy = re.compile(
            r"^\s*COPY\s+\.\s+", re.MULTILINE
        )
        self.assertTrue(
            package_copy.search(text),
            "Dockerfile must use 'COPY . <dest>' to include the full backend "
            "package in the image (not just app.py).",
        )


class BackendDockerfileEntrypointTest(unittest.TestCase):
    """The Dockerfile CMD must use module mode so `backend.*` imports resolve."""

    def test_entrypoint_uses_module_mode(self):
        """CMD must run python3 -m backend.app, not python3 app.py."""
        text = _dockerfile_text()
        bare_script = re.compile(
            r'CMD\s+\["python3",\s*"app\.py"\]', re.MULTILINE
        )
        self.assertFalse(
            bare_script.search(text),
            "Dockerfile CMD must not be 'python3 app.py'; use "
            "'python3 -m backend.app' so the backend package is on sys.path.",
        )

    def test_entrypoint_is_module_backend_app(self):
        """CMD must reference backend.app as a module."""
        text = _dockerfile_text()
        module_cmd = re.compile(
            r'CMD\s+\[.*"-m",\s*"backend\.app".*\]', re.MULTILINE
        )
        self.assertTrue(
            module_cmd.search(text),
            "Dockerfile CMD must use module-mode entrypoint: "
            '["python3", "-m", "backend.app"]',
        )


class BackendPackageImportSmokeTest(unittest.TestCase):
    """Source-level smoke: backend.health must be importable from the repo root."""

    def test_backend_health_importable_as_package(self):
        """Importing backend.health must succeed without sys.path manipulation."""
        try:
            import importlib
            spec = importlib.util.find_spec("backend.health")
            self.assertIsNotNone(
                spec,
                "backend.health is not findable as a package. "
                "Ensure backend/__init__.py exists and the package is on sys.path.",
            )
        except ModuleNotFoundError as exc:
            self.fail(f"backend.health could not be imported: {exc}")


class BackendDockerfileCompilerTest(unittest.TestCase):
    """Dockerfile deve usar ubuntu como base e compilar simplesc."""

    def test_base_image_is_ubuntu(self):
        """FROM deve usar ubuntu (não python:*-slim)."""
        text = _dockerfile_text()
        self.assertIn(
            "ubuntu",
            text,
            "Dockerfile base image must be ubuntu (not python:3.12-slim) "
            "so build-essential is available for compiling simplesc.",
        )

    def test_simplesc_binary_is_installed(self):
        """Dockerfile deve copiar simples-compiler e instalar o binário."""
        text = _dockerfile_text()
        self.assertIn(
            "simples-compiler",
            text,
            "Dockerfile must COPY simples-compiler source tree.",
        )
        self.assertIn(
            "simplesc",
            text,
            "Dockerfile must install simplesc binary (cp simplesc /usr/local/bin/simplesc).",
        )

    def test_build_essential_installed(self):
        """Dockerfile deve instalar build-essential para compilar simplesc."""
        text = _dockerfile_text()
        self.assertIn(
            "build-essential",
            text,
            "Dockerfile must install build-essential to compile the simplesc C source.",
        )


if __name__ == "__main__":
    unittest.main()
