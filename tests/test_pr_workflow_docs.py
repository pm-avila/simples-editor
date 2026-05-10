import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PrWorkflowDocsFoundationTest(unittest.TestCase):
    def test_required_pr_workflow_files_exist(self):
        required = [
            ROOT / "docs" / "team-roster.md",
            ROOT / "docs" / "pr-workflow.md",
            ROOT / "tests" / "test_pr_workflow_docs.py",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing: {path}")

    def test_team_roster_declares_pm_avila(self):
        content = (ROOT / "docs" / "team-roster.md").read_text(encoding="utf-8")
        self.assertIn("pm-avila", content)

    def test_pr_workflow_documents_branch_review_and_merge(self):
        content = (ROOT / "docs" / "pr-workflow.md").read_text(encoding="utf-8")
        self.assertIn("feat/", content)
        self.assertIn("review", content.lower())
        self.assertIn("merge", content.lower())
        self.assertIn("dev", content)


if __name__ == "__main__":
    unittest.main()
