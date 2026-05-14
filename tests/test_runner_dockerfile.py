import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "runner" / "Dockerfile"


def _dockerfile_text():
    return DOCKERFILE.read_text(encoding="utf-8")


class RunnerDockerfileContractTest(unittest.TestCase):
    def test_base_image_is_debian_slim(self):
        text = _dockerfile_text()
        self.assertRegex(text, re.compile(r"^\s*FROM\s+debian:[^\s]*slim", re.MULTILINE))

    def test_qemu_user_static_is_installed(self):
        text = _dockerfile_text()
        self.assertIn("qemu-user-static", text)

    def test_non_root_sandbox_user_is_configured(self):
        text = _dockerfile_text()
        self.assertIn("useradd", text)
        self.assertIn("sandbox", text)
        self.assertRegex(text, re.compile(r"^\s*USER\s+sandbox\s*$", re.MULTILINE))

    def test_workdir_is_sandbox(self):
        text = _dockerfile_text()
        self.assertRegex(text, re.compile(r"^\s*WORKDIR\s+/sandbox\s*$", re.MULTILINE))


if __name__ == "__main__":
    unittest.main()
