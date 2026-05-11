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

    def test_ide_shell_is_reachable_at_ide_route(self):
        router = (ROOT / "frontend" / "src" / "router.tsx").read_text(encoding="utf-8")
        self.assertIn('path: "/ide"', router, "router must expose an /ide route")
        self.assertIn("IdeShell", router, "IdeShell component must be wired to the /ide route")


if __name__ == "__main__":
    unittest.main()
