import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class MonacoMainRouteTest(unittest.TestCase):
    def test_monaco_component_and_router_files_exist(self):
        required = [
            ROOT / "frontend" / "src" / "router.tsx",
            ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx",
            ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_monaco_editor_is_wired_to_the_main_ide_route(self):
        router = (ROOT / "frontend" / "src" / "router.tsx").read_text(encoding="utf-8")
        shell = (ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx").read_text(encoding="utf-8")
        editor = (ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx").read_text(encoding="utf-8")
        self.assertIn('path: "/"', router)
        self.assertIn("MonacoEditorPane", shell)
        self.assertIn("@monaco-editor/react", editor)
        self.assertIn("defaultLanguage", editor)
        self.assertIn("onChange", editor)

    def test_ide_shell_rendered_by_auth_gate_not_public_route(self):
        router = (ROOT / "frontend" / "src" / "router.tsx").read_text(encoding="utf-8")
        app = (ROOT / "frontend" / "src" / "app.tsx").read_text(encoding="utf-8")
        self.assertNotIn('path: "/ide"', router, "IDE must not be on a public /ide route")
        self.assertIn("IdeShell", app, "IdeShell must be rendered by App's auth gate")


class ReadmeContractTest(unittest.TestCase):
    """Regression guard: README claims are cross-checked against real source/build files."""

    def setUp(self):
        self._readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_readme_mentions_monaco_and_source_uses_monaco_editor_react(self):
        self.assertIn("Monaco", self._readme, "README must mention Monaco editor")
        editor_pane = (
            ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "@monaco-editor/react",
            editor_pane,
            "monaco-editor-pane.tsx must import @monaco-editor/react",
        )

    def test_readme_mentions_npm_run_build_and_package_json_has_build_script(self):
        self.assertIn("npm run build", self._readme, "README must document the frontend build command")
        import json
        pkg = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        self.assertIn(
            "build",
            pkg.get("scripts", {}),
            "frontend/package.json must define a 'build' script",
        )

    def test_readme_describes_react_typescript_frontend(self):
        readme = self._readme.lower()
        self.assertIn("react", readme, "README must mention React")
        self.assertIn("typescript", readme, "README must mention TypeScript")

    def test_readme_explains_auth_gated_ide_and_app_implements_auth_gate(self):
        self.assertIn("IdeShell", self._readme, "README must mention IdeShell (auth-gated IDE route)")
        app = (ROOT / "frontend" / "src" / "app.tsx").read_text(encoding="utf-8")
        self.assertIn("getSession", app, "app.tsx must use getSession for auth check")
        self.assertIn(
            "signInWithPassword", app, "app.tsx must use signInWithPassword for login"
        )
        self.assertIn("IdeShell", app, "app.tsx must render IdeShell for authenticated users")


if __name__ == "__main__":
    unittest.main()
