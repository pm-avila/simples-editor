import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SimplesThemeContractTest(unittest.TestCase):
    def test_simples_theme_module_exists(self):
        path = ROOT / "frontend" / "src" / "components" / "ide" / "simples-theme.ts"
        self.assertTrue(path.exists(), f"missing: {path}")

    def test_theme_id_constant_present(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "simples-theme.ts"
        ).read_text(encoding="utf-8")
        self.assertIn('SIMPLES_THEME_ID = "simples-dark"', content)

    def test_token_colour_rules_present(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "simples-theme.ts"
        ).read_text(encoding="utf-8")
        self.assertIn("4FC1FF", content)   # keyword cyan
        self.assertIn("FFB347", content)   # number orange
        self.assertIn("D4D4D4", content)   # identifier neutral


class SimplesThemeIntegrationTest(unittest.TestCase):
    def test_editor_uses_theme_constant(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "monaco-editor-pane.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("defineSimplesDarkTheme", content)
        self.assertIn("SIMPLES_THEME_ID", content)
        self.assertIn("theme={SIMPLES_THEME_ID}", content)


if __name__ == "__main__":
    unittest.main()
