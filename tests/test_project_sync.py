"""Tests for project_sync.py - Sprint 1 kanban automation core."""

import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from project_sync import (
    is_sprint1_eligible,
    determine_status,
    _extract_linked_issue_number,
    _get_project_meta,
    _find_or_add_item,
)


class TestSprint1Eligibility(unittest.TestCase):

    def _make_issue(self, milestone_title=None, labels=None):
        issue = {"state": "open", "labels": [], "milestone": None}
        if milestone_title:
            issue["milestone"] = {"title": milestone_title}
        if labels:
            issue["labels"] = [{"name": l} for l in labels]
        return issue

    def test_eligible_by_sprint1_milestone(self):
        issue = self._make_issue(milestone_title="Sprint 1")
        self.assertTrue(is_sprint1_eligible(issue))

    def test_eligible_by_sprint1_label(self):
        issue = self._make_issue(labels=["sprint-1"])
        self.assertTrue(is_sprint1_eligible(issue))

    def test_not_eligible_with_sprint2_milestone(self):
        issue = self._make_issue(milestone_title="Sprint 2")
        self.assertFalse(is_sprint1_eligible(issue))

    def test_not_eligible_with_no_milestone_or_label(self):
        issue = self._make_issue()
        self.assertFalse(is_sprint1_eligible(issue))

    def test_not_eligible_with_unrelated_label(self):
        issue = self._make_issue(labels=["bug", "enhancement"])
        self.assertFalse(is_sprint1_eligible(issue))


class TestStatusMapping(unittest.TestCase):

    def _open_issue(self):
        return {"state": "open", "labels": [], "milestone": None}

    def _closed_issue(self):
        return {"state": "closed", "labels": [], "milestone": None}

    def _draft_pr(self):
        return {"state": "open", "draft": True}

    def _ready_pr(self):
        return {"state": "open", "draft": False}

    def test_backlog_open_issue_no_pr(self):
        self.assertEqual(determine_status(self._open_issue(), pr=None), "Backlog")

    def test_in_progress_open_issue_with_draft_pr(self):
        self.assertEqual(
            determine_status(self._open_issue(), pr=self._draft_pr()), "In progress"
        )

    def test_in_review_open_issue_with_ready_pr(self):
        self.assertEqual(
            determine_status(self._open_issue(), pr=self._ready_pr()), "In review"
        )

    def test_raises_if_pr_missing_draft_field(self):
        """PR dict without a 'draft' key is malformed — must raise, not silently default."""
        pr_without_draft = {"state": "open"}
        with self.assertRaises(RuntimeError):
            determine_status(self._open_issue(), pr=pr_without_draft)

    def test_done_closed_issue(self):
        self.assertEqual(determine_status(self._closed_issue(), pr=None), "Done")

    def test_done_closed_issue_ignores_pr(self):
        """Closed issue is Done regardless of PR state."""
        self.assertEqual(
            determine_status(self._closed_issue(), pr=self._ready_pr()), "Done"
        )


class TestExtractLinkedIssueNumber(unittest.TestCase):
    """Unit tests for _extract_linked_issue_number."""

    def _pr(self, body="", title=""):
        return {"state": "open", "draft": False, "body": body, "title": title}

    def test_extracts_closes_reference(self):
        pr = self._pr(body="Closes #42.")
        self.assertEqual(_extract_linked_issue_number(pr), 42)

    def test_extracts_fixes_reference(self):
        pr = self._pr(body="fixes #7 in this commit")
        self.assertEqual(_extract_linked_issue_number(pr), 7)

    def test_extracts_resolves_reference(self):
        pr = self._pr(body="Resolves #100")
        self.assertEqual(_extract_linked_issue_number(pr), 100)

    def test_case_insensitive_matching(self):
        pr = self._pr(body="CLOSES #5")
        self.assertEqual(_extract_linked_issue_number(pr), 5)

    def test_raises_if_no_linked_issue_reference(self):
        pr = self._pr(body="No reference here — just a general PR")
        with self.assertRaises(RuntimeError):
            _extract_linked_issue_number(pr)

    def test_raises_if_body_is_none(self):
        pr = {"state": "open", "draft": False, "body": None, "title": "fix: something"}
        with self.assertRaises(RuntimeError):
            _extract_linked_issue_number(pr)

    def test_raises_if_body_is_empty(self):
        pr = self._pr(body="")
        with self.assertRaises(RuntimeError):
            _extract_linked_issue_number(pr)

    def test_extracts_first_reference_when_multiple(self):
        pr = self._pr(body="Closes #10. Also related to #20.")
        self.assertEqual(_extract_linked_issue_number(pr), 10)


class TestRun(unittest.TestCase):
    """Integration tests for run() — mocks external I/O only."""

    _REPO = "pm-avila/test-repo"
    _PROJECT_META = ("P_id", "F_id", {
        "Backlog": "opt_backlog",
        "In progress": "opt_in_progress",
        "In review": "opt_in_review",
        "Done": "opt_done",
    })

    def _sprint1_issue(self, number=1, state="open", node_id="I_node_1"):
        return {
            "number": number,
            "state": state,
            "node_id": node_id,
            "labels": [{"name": "sprint-1"}],
            "milestone": None,
        }

    def _non_sprint1_issue(self, number=2):
        return {
            "number": number,
            "state": "open",
            "node_id": "I_node_2",
            "labels": [],
            "milestone": None,
        }

    def _pr_payload(self, draft=False, body="Closes #1"):
        return {
            "number": 10,
            "state": "open",
            "draft": draft,
            "body": body,
            "title": "fix: something",
            "node_id": "PR_node_10",
        }

    def _env(self):
        return {"GITHUB_REPOSITORY": self._REPO, "GH_TOKEN": "fake_token"}

    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item", return_value="item_id")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._load_event")
    def test_run_issue_event_open_issue_gives_backlog(
        self, mock_load, mock_meta, mock_find, mock_update
    ):
        """issue event with open Sprint-1 issue and no PR → Backlog."""
        mock_load.return_value = {"issue": self._sprint1_issue()}
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_update.assert_called_once_with("P_id", "item_id", "F_id", "opt_backlog")

    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item", return_value="item_id")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._load_event")
    def test_run_issue_event_closed_issue_gives_done(
        self, mock_load, mock_meta, mock_find, mock_update
    ):
        """issue event with closed Sprint-1 issue → Done."""
        mock_load.return_value = {"issue": self._sprint1_issue(state="closed")}
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_update.assert_called_once_with("P_id", "item_id", "F_id", "opt_done")

    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item", return_value="item_id")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._fetch_issue")
    @patch("project_sync._load_event")
    def test_run_pull_request_event_ready_pr_gives_in_review(
        self, mock_load, mock_fetch, mock_meta, mock_find, mock_update
    ):
        """pull_request event with non-draft PR and Sprint-1 linked issue → In review."""
        pr = self._pr_payload(draft=False, body="Closes #1")
        mock_load.return_value = {"pull_request": pr}
        mock_fetch.return_value = self._sprint1_issue(number=1)
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_fetch.assert_called_once_with(1, self._REPO)
        mock_update.assert_called_once_with("P_id", "item_id", "F_id", "opt_in_review")

    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item", return_value="item_id")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._fetch_issue")
    @patch("project_sync._load_event")
    def test_run_pull_request_event_draft_pr_gives_in_progress(
        self, mock_load, mock_fetch, mock_meta, mock_find, mock_update
    ):
        """pull_request event with draft PR and Sprint-1 linked issue → In progress."""
        pr = self._pr_payload(draft=True, body="Fixes #1")
        mock_load.return_value = {"pull_request": pr}
        mock_fetch.return_value = self._sprint1_issue(number=1)
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_fetch.assert_called_once_with(1, self._REPO)
        mock_update.assert_called_once_with("P_id", "item_id", "F_id", "opt_in_progress")

    @patch("project_sync._load_event")
    def test_run_unsupported_event_raises(self, mock_load):
        """Event payload with neither 'issue' nor 'pull_request' → RuntimeError."""
        mock_load.return_value = {"release": {"tag_name": "v1.0"}}

        import project_sync
        with patch.dict(os.environ, self._env()):
            with self.assertRaises(RuntimeError):
                project_sync.run()

    @patch("project_sync._load_event")
    def test_run_pull_request_event_no_linked_issue_raises(self, mock_load):
        """pull_request event whose body has no Closes/Fixes/Resolves #N → RuntimeError."""
        pr = self._pr_payload(draft=False, body="General refactor, no linked issue")
        mock_load.return_value = {"pull_request": pr}

        import project_sync
        with patch.dict(os.environ, self._env()):
            with self.assertRaises(RuntimeError):
                project_sync.run()

    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._fetch_issue")
    @patch("project_sync._load_event")
    def test_run_pull_request_event_non_sprint1_skips(
        self, mock_load, mock_fetch, mock_meta, mock_find, mock_update
    ):
        """pull_request event whose linked issue is not Sprint-1 → skip (no status update)."""
        pr = self._pr_payload(draft=False, body="Closes #2")
        mock_load.return_value = {"pull_request": pr}
        mock_fetch.return_value = self._non_sprint1_issue(number=2)

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_meta.assert_not_called()
        mock_update.assert_not_called()

    @patch("project_sync._load_event")
    def test_run_missing_github_repository_raises(self, mock_load):
        """Missing GITHUB_REPOSITORY env var → RuntimeError for any event type."""
        mock_load.return_value = {"issue": self._sprint1_issue()}

        import project_sync
        env_without_repo = {"GH_TOKEN": "fake_token"}
        with patch.dict(os.environ, env_without_repo, clear=False):
            env_copy = os.environ.copy()
            env_copy.pop("GITHUB_REPOSITORY", None)
            with patch.dict(os.environ, env_copy, clear=True):
                with self.assertRaises(RuntimeError):
                    project_sync.run()


class TestGetProjectMetaShapeValidation(unittest.TestCase):
    """_get_project_meta must raise RuntimeError on unexpected GraphQL response shapes."""

    @patch("project_sync._graphql")
    def test_raises_when_user_is_null(self, mock_graphql):
        """GraphQL returns user: null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.return_value = {"user": None}
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("user", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_projectv2_is_null(self, mock_graphql):
        """GraphQL returns projectV2: null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.return_value = {"user": {"projectV2": None}}
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("project", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_fields_is_null(self, mock_graphql):
        """GraphQL returns fields: null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.return_value = {"user": {"projectV2": {"id": "P_id", "fields": None}}}
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("fields", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_fields_nodes_is_null(self, mock_graphql):
        """GraphQL returns fields.nodes: null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.return_value = {
            "user": {"projectV2": {"id": "P_id", "fields": {"nodes": None}}}
        }
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("fields", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_status_field_options_missing(self, mock_graphql):
        """Status field lacks 'options' key → explicit RuntimeError, not raw KeyError."""
        mock_graphql.return_value = {
            "user": {
                "projectV2": {
                    "id": "P_id",
                    "fields": {
                        "nodes": [{"name": "Status"}]  # 'options' key absent
                    },
                }
            }
        }
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("options", str(cm.exception).lower())


class TestFindOrAddItemShapeValidation(unittest.TestCase):
    """_find_or_add_item must raise RuntimeError on unexpected GraphQL response shapes."""

    @patch("project_sync._graphql")
    def test_raises_when_node_is_null(self, mock_graphql):
        """GraphQL returns node: null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.return_value = {"node": None}
        with self.assertRaises(RuntimeError) as cm:
            _find_or_add_item("P_id", "I_node_1")
        self.assertIn("node", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_node_items_is_null(self, mock_graphql):
        """GraphQL returns node.items: null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.return_value = {"node": {"items": None}}
        with self.assertRaises(RuntimeError) as cm:
            _find_or_add_item("P_id", "I_node_1")
        self.assertIn("items", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_node_items_nodes_is_null(self, mock_graphql):
        """GraphQL returns node.items.nodes: null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.return_value = {"node": {"items": {"nodes": None}}}
        with self.assertRaises(RuntimeError) as cm:
            _find_or_add_item("P_id", "I_node_1")
        self.assertIn("nodes", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_add_item_mutation_returns_null(self, mock_graphql):
        """addProjectV2ItemById returns null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.side_effect = [
            {"node": {"items": {"nodes": []}}},   # query: item not found
            {"addProjectV2ItemById": None},         # mutation: null result
        ]
        with self.assertRaises(RuntimeError) as cm:
            _find_or_add_item("P_id", "I_node_1")
        self.assertIn("addprojectv2itembyid", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_add_item_mutation_item_is_null(self, mock_graphql):
        """addProjectV2ItemById.item is null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.side_effect = [
            {"node": {"items": {"nodes": []}}},        # query: item not found
            {"addProjectV2ItemById": {"item": None}},  # mutation: item null
        ]
        with self.assertRaises(RuntimeError) as cm:
            _find_or_add_item("P_id", "I_node_1")
        self.assertIn("item", str(cm.exception).lower())


class TestRunNodeIdValidation(unittest.TestCase):
    """run() must raise explicitly when the issue REST payload lacks node_id."""

    _REPO = "pm-avila/test-repo"
    _PROJECT_META = ("P_id", "F_id", {
        "Backlog": "opt_backlog",
        "In progress": "opt_in_progress",
        "In review": "opt_in_review",
        "Done": "opt_done",
    })

    def _sprint1_issue_no_node_id(self, number=1, state="open"):
        return {
            "number": number,
            "state": state,
            "labels": [{"name": "sprint-1"}],
            "milestone": None,
            # node_id deliberately absent
        }

    @patch("project_sync._get_project_meta")
    @patch("project_sync._load_event")
    def test_run_raises_when_issue_missing_node_id(self, mock_load, mock_meta):
        """Sprint-1 issue missing node_id → explicit RuntimeError instead of raw KeyError."""
        mock_load.return_value = {"issue": self._sprint1_issue_no_node_id()}
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        env = {"GITHUB_REPOSITORY": self._REPO, "GH_TOKEN": "fake_token"}
        with patch.dict(os.environ, env):
            with self.assertRaises(RuntimeError) as cm:
                project_sync.run()
        self.assertIn("node_id", str(cm.exception).lower())


if __name__ == "__main__":
    unittest.main()
