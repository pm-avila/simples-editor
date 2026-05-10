"""Tests for project_sync.py - Sprint 1 kanban automation core."""

import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from project_sync import (
    is_sprint1_eligible,
    determine_status,
    _extract_linked_issue_number,
    _get_project_meta,
    _find_or_add_item,
    _graphql,
    _fetch_linked_pr_for_issue,
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
    @patch("project_sync._fetch_linked_pr_for_issue", return_value=None)
    @patch("project_sync._load_event")
    def test_run_issue_event_open_issue_gives_backlog(
        self, mock_load, mock_fetch_pr, mock_meta, mock_find, mock_update
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
            {"node": {"items": {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}}},
            {"addProjectV2ItemById": None},         # mutation: null result
        ]
        with self.assertRaises(RuntimeError) as cm:
            _find_or_add_item("P_id", "I_node_1")
        self.assertIn("addprojectv2itembyid", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_add_item_mutation_item_is_null(self, mock_graphql):
        """addProjectV2ItemById.item is null → explicit RuntimeError, not raw TypeError."""
        mock_graphql.side_effect = [
            {"node": {"items": {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}}},
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

    @patch("project_sync._fetch_linked_pr_for_issue", return_value=None)
    @patch("project_sync._get_project_meta")
    @patch("project_sync._load_event")
    def test_run_raises_when_issue_missing_node_id(self, mock_load, mock_meta, mock_fetch_pr):
        """Sprint-1 issue missing node_id → explicit RuntimeError instead of raw KeyError."""
        mock_load.return_value = {"issue": self._sprint1_issue_no_node_id()}
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        env = {"GITHUB_REPOSITORY": self._REPO, "GH_TOKEN": "fake_token"}
        with patch.dict(os.environ, env):
            with self.assertRaises(RuntimeError) as cm:
                project_sync.run()
        self.assertIn("node_id", str(cm.exception).lower())


class TestGraphQLMissingDataKey(unittest.TestCase):
    """_graphql must raise RuntimeError when the JSON response lacks a 'data' key."""

    @patch("urllib.request.urlopen")
    @patch("project_sync._gh_token", return_value="fake_token")
    def test_raises_when_response_has_no_data_key(self, mock_token, mock_urlopen):
        """GraphQL JSON without 'data' key → explicit RuntimeError, not raw KeyError."""
        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=ctx)
        ctx.__exit__ = MagicMock(return_value=False)
        ctx.read.return_value = json.dumps({"status": "ok"}).encode()
        mock_urlopen.return_value = ctx
        with self.assertRaises(RuntimeError) as cm:
            _graphql("query { viewer { login } }")
        self.assertIn("data", str(cm.exception).lower())


class TestGetProjectMetaIdFieldValidation(unittest.TestCase):
    """_get_project_meta must raise RuntimeError when 'id' fields are missing in API response."""

    @patch("project_sync._graphql")
    def test_raises_when_project_id_missing(self, mock_graphql):
        """projectV2 node has no 'id' key → explicit RuntimeError, not raw KeyError."""
        mock_graphql.return_value = {
            "user": {
                "projectV2": {
                    # 'id' key deliberately absent
                    "fields": {"nodes": []},
                }
            }
        }
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("id", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_status_field_id_missing(self, mock_graphql):
        """Status field has no 'id' key → explicit RuntimeError, not raw KeyError."""
        mock_graphql.return_value = {
            "user": {
                "projectV2": {
                    "id": "P_id",
                    "fields": {
                        "nodes": [
                            {
                                # 'id' key deliberately absent from status field
                                "name": "Status",
                                "options": [{"name": "Backlog", "id": "opt1"}],
                            }
                        ]
                    },
                }
            }
        }
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("id", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_option_missing_id(self, mock_graphql):
        """Option in Status field has no 'id' key → explicit RuntimeError, not raw KeyError."""
        mock_graphql.return_value = {
            "user": {
                "projectV2": {
                    "id": "P_id",
                    "fields": {
                        "nodes": [
                            {
                                "id": "F_id",
                                "name": "Status",
                                "options": [{"name": "Backlog"}],  # 'id' absent
                            }
                        ]
                    },
                }
            }
        }
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("option", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_option_missing_name(self, mock_graphql):
        """Option in Status field has no 'name' key → explicit RuntimeError, not raw KeyError."""
        mock_graphql.return_value = {
            "user": {
                "projectV2": {
                    "id": "P_id",
                    "fields": {
                        "nodes": [
                            {
                                "id": "F_id",
                                "name": "Status",
                                "options": [{"id": "opt1"}],  # 'name' absent
                            }
                        ]
                    },
                }
            }
        }
        with self.assertRaises(RuntimeError) as cm:
            _get_project_meta()
        self.assertIn("option", str(cm.exception).lower())


class TestFindOrAddItemIdFieldValidation(unittest.TestCase):
    """_find_or_add_item must raise RuntimeError when item 'id' is missing in API response."""

    @patch("project_sync._graphql")
    def test_raises_when_existing_item_lacks_id(self, mock_graphql):
        """Matching item in project has no 'id' key → explicit RuntimeError, not raw KeyError."""
        mock_graphql.return_value = {
            "node": {
                "items": {
                    "nodes": [
                        {
                            # 'id' key deliberately absent
                            "content": {"id": "I_node_1"},
                        }
                    ]
                }
            }
        }
        with self.assertRaises(RuntimeError) as cm:
            _find_or_add_item("P_id", "I_node_1")
        self.assertIn("id", str(cm.exception).lower())

    @patch("project_sync._graphql")
    def test_raises_when_mutation_item_lacks_id(self, mock_graphql):
        """Mutation returns item with no 'id' key → explicit RuntimeError, not raw KeyError."""
        mock_graphql.side_effect = [
            {"node": {"items": {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}}},
            {"addProjectV2ItemById": {"item": {"name": "x"}}},   # mutation: item without id
        ]
        with self.assertRaises(RuntimeError) as cm:
            _find_or_add_item("P_id", "I_node_1")
        self.assertIn("id", str(cm.exception).lower())


class TestFetchLinkedPrForIssue(unittest.TestCase):
    """Unit tests for _fetch_linked_pr_for_issue."""

    def _pr(self, number, body, draft=False):
        return {
            "number": number,
            "state": "open",
            "draft": draft,
            "body": body,
            "title": f"PR #{number}",
            "node_id": f"PR_node_{number}",
        }

    @patch("project_sync._api_request")
    def test_returns_none_when_no_open_prs(self, mock_api):
        mock_api.return_value = []
        result = _fetch_linked_pr_for_issue(1, "owner/repo")
        self.assertIsNone(result)

    @patch("project_sync._api_request")
    def test_returns_none_when_no_pr_references_issue(self, mock_api):
        mock_api.return_value = [self._pr(10, "General refactor, no linked issue")]
        result = _fetch_linked_pr_for_issue(1, "owner/repo")
        self.assertIsNone(result)

    @patch("project_sync._api_request")
    def test_returns_pr_when_closes_references_issue(self, mock_api):
        pr = self._pr(10, "Closes #5")
        mock_api.return_value = [pr]
        result = _fetch_linked_pr_for_issue(5, "owner/repo")
        self.assertEqual(result["number"], 10)

    @patch("project_sync._api_request")
    def test_returns_pr_when_fixes_references_issue(self, mock_api):
        pr = self._pr(10, "Fixes #5")
        mock_api.return_value = [pr]
        result = _fetch_linked_pr_for_issue(5, "owner/repo")
        self.assertEqual(result["number"], 10)

    @patch("project_sync._api_request")
    def test_returns_pr_when_resolves_references_issue(self, mock_api):
        pr = self._pr(10, "Resolves #5")
        mock_api.return_value = [pr]
        result = _fetch_linked_pr_for_issue(5, "owner/repo")
        self.assertEqual(result["number"], 10)

    @patch("project_sync._api_request")
    def test_returns_first_matching_pr_when_multiple_match(self, mock_api):
        mock_api.return_value = [
            self._pr(10, "Closes #5"),
            self._pr(11, "Fixes #5"),
        ]
        result = _fetch_linked_pr_for_issue(5, "owner/repo")
        self.assertEqual(result["number"], 10)

    @patch("project_sync._api_request")
    def test_returned_pr_preserves_draft_field(self, mock_api):
        pr = self._pr(10, "Closes #5", draft=True)
        mock_api.return_value = [pr]
        result = _fetch_linked_pr_for_issue(5, "owner/repo")
        self.assertIsNotNone(result)
        self.assertTrue(result["draft"])

    @patch("project_sync._api_request")
    def test_does_not_match_pr_referencing_different_issue(self, mock_api):
        mock_api.return_value = [self._pr(10, "Closes #99")]
        result = _fetch_linked_pr_for_issue(5, "owner/repo")
        self.assertIsNone(result)

    @patch("project_sync._api_request")
    def test_raises_on_invalid_repo_format(self, mock_api):
        with self.assertRaises(RuntimeError):
            _fetch_linked_pr_for_issue(1, "bad-repo-no-slash")


class TestRunIssueEventActiveLinkedPR(unittest.TestCase):
    """run() must not downgrade status when an open Sprint-1 issue has an active linked PR."""

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

    def _active_ready_pr(self, issue_number=1):
        return {
            "number": 10,
            "state": "open",
            "draft": False,
            "body": f"Closes #{issue_number}",
            "title": "fix: something",
            "node_id": "PR_node_10",
        }

    def _active_draft_pr(self, issue_number=1):
        return {
            "number": 10,
            "state": "open",
            "draft": True,
            "body": f"Closes #{issue_number}",
            "title": "fix: something",
            "node_id": "PR_node_10",
        }

    def _env(self):
        return {"GITHUB_REPOSITORY": self._REPO, "GH_TOKEN": "fake_token"}

    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item", return_value="item_id")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._fetch_linked_pr_for_issue")
    @patch("project_sync._load_event")
    def test_issue_event_open_sprint1_with_active_ready_pr_gives_in_review(
        self, mock_load, mock_fetch_pr, mock_meta, mock_find, mock_update
    ):
        """issue event + open Sprint-1 issue + active non-draft linked PR → In review."""
        mock_load.return_value = {"issue": self._sprint1_issue()}
        mock_fetch_pr.return_value = self._active_ready_pr(issue_number=1)
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_update.assert_called_once_with("P_id", "item_id", "F_id", "opt_in_review")

    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item", return_value="item_id")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._fetch_linked_pr_for_issue")
    @patch("project_sync._load_event")
    def test_issue_event_open_sprint1_with_active_draft_pr_gives_in_progress(
        self, mock_load, mock_fetch_pr, mock_meta, mock_find, mock_update
    ):
        """issue event + open Sprint-1 issue + active draft linked PR → In progress."""
        mock_load.return_value = {"issue": self._sprint1_issue()}
        mock_fetch_pr.return_value = self._active_draft_pr(issue_number=1)
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_update.assert_called_once_with("P_id", "item_id", "F_id", "opt_in_progress")

    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item", return_value="item_id")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._fetch_linked_pr_for_issue")
    @patch("project_sync._load_event")
    def test_issue_event_open_sprint1_no_linked_pr_still_gives_backlog(
        self, mock_load, mock_fetch_pr, mock_meta, mock_find, mock_update
    ):
        """issue event + open Sprint-1 issue + no active linked PR → Backlog (unchanged)."""
        mock_load.return_value = {"issue": self._sprint1_issue()}
        mock_fetch_pr.return_value = None
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_update.assert_called_once_with("P_id", "item_id", "F_id", "opt_backlog")

    @patch("project_sync._fetch_linked_pr_for_issue")
    @patch("project_sync._update_status")
    @patch("project_sync._find_or_add_item", return_value="item_id")
    @patch("project_sync._get_project_meta")
    @patch("project_sync._load_event")
    def test_issue_event_closed_sprint1_does_not_call_fetch_linked_pr(
        self, mock_load, mock_meta, mock_find, mock_update, mock_fetch_pr
    ):
        """issue event + closed Sprint-1 issue → Done, no PR lookup needed."""
        mock_load.return_value = {"issue": self._sprint1_issue(state="closed")}
        mock_meta.return_value = self._PROJECT_META

        import project_sync
        with patch.dict(os.environ, self._env()):
            project_sync.run()

        mock_fetch_pr.assert_not_called()
        mock_update.assert_called_once_with("P_id", "item_id", "F_id", "opt_done")


class TestCloseKeywordVariants(unittest.TestCase):
    """_extract_linked_issue_number and _fetch_linked_pr_for_issue must accept
    all GitHub close-keyword variants: close/closed/fix/fixed/resolve/resolved."""

    def _pr(self, body):
        return {"state": "open", "draft": False, "body": body, "title": "t"}

    # --- _extract_linked_issue_number ---

    def test_extract_closed_variant(self):
        self.assertEqual(_extract_linked_issue_number(self._pr("Closed #3")), 3)

    def test_extract_close_variant(self):
        self.assertEqual(_extract_linked_issue_number(self._pr("close #8")), 8)

    def test_extract_fixed_variant(self):
        self.assertEqual(_extract_linked_issue_number(self._pr("Fixed #11")), 11)

    def test_extract_fix_variant(self):
        self.assertEqual(_extract_linked_issue_number(self._pr("fix #2")), 2)

    def test_extract_resolved_variant(self):
        self.assertEqual(_extract_linked_issue_number(self._pr("Resolved #15")), 15)

    def test_extract_resolve_variant(self):
        self.assertEqual(_extract_linked_issue_number(self._pr("resolve #9")), 9)

    # --- _fetch_linked_pr_for_issue ---

    def _api_pr(self, number, body):
        return {"number": number, "state": "open", "draft": False, "body": body,
                "title": f"PR #{number}", "node_id": f"PR_node_{number}"}

    @patch("project_sync._api_request")
    def test_fetch_pr_closed_variant(self, mock_api):
        pr = self._api_pr(10, "Closed #5")
        mock_api.return_value = [pr]
        self.assertEqual(_fetch_linked_pr_for_issue(5, "owner/repo")["number"], 10)

    @patch("project_sync._api_request")
    def test_fetch_pr_close_variant(self, mock_api):
        pr = self._api_pr(10, "close #5")
        mock_api.return_value = [pr]
        self.assertEqual(_fetch_linked_pr_for_issue(5, "owner/repo")["number"], 10)

    @patch("project_sync._api_request")
    def test_fetch_pr_fixed_variant(self, mock_api):
        pr = self._api_pr(10, "Fixed #5")
        mock_api.return_value = [pr]
        self.assertEqual(_fetch_linked_pr_for_issue(5, "owner/repo")["number"], 10)

    @patch("project_sync._api_request")
    def test_fetch_pr_fix_variant(self, mock_api):
        pr = self._api_pr(10, "fix #5")
        mock_api.return_value = [pr]
        self.assertEqual(_fetch_linked_pr_for_issue(5, "owner/repo")["number"], 10)

    @patch("project_sync._api_request")
    def test_fetch_pr_resolved_variant(self, mock_api):
        pr = self._api_pr(10, "Resolved #5")
        mock_api.return_value = [pr]
        self.assertEqual(_fetch_linked_pr_for_issue(5, "owner/repo")["number"], 10)

    @patch("project_sync._api_request")
    def test_fetch_pr_resolve_variant(self, mock_api):
        pr = self._api_pr(10, "resolve #5")
        mock_api.return_value = [pr]
        self.assertEqual(_fetch_linked_pr_for_issue(5, "owner/repo")["number"], 10)


class TestFindOrAddItemPagination(unittest.TestCase):
    """_find_or_add_item must paginate over all Project items before adding."""

    def _item(self, item_id, issue_id):
        return {"id": item_id, "content": {"id": issue_id}}

    def _page(self, nodes, has_next=False, cursor=None):
        return {
            "node": {
                "items": {
                    "nodes": nodes,
                    "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
                }
            }
        }

    @patch("project_sync._graphql")
    def test_finds_item_on_second_page(self, mock_graphql):
        """Issue is on page 2 — must not add a duplicate, must return its item_id."""
        page1 = self._page(
            [self._item("item_other", "I_other")],
            has_next=True,
            cursor="cursor_abc",
        )
        page2 = self._page(
            [self._item("item_target", "I_target")],
            has_next=False,
            cursor=None,
        )
        mock_graphql.side_effect = [page1, page2]
        result = _find_or_add_item("P_id", "I_target")
        self.assertEqual(result, "item_target")
        # Must NOT have called mutation (add) since item was found
        self.assertEqual(mock_graphql.call_count, 2)

    @patch("project_sync._graphql")
    def test_adds_item_after_exhausting_all_pages(self, mock_graphql):
        """Issue absent on every page — must add after pagination ends."""
        page1 = self._page(
            [self._item("item_other", "I_other")],
            has_next=True,
            cursor="cursor_abc",
        )
        page2 = self._page([], has_next=False, cursor=None)
        mutation_result = {"addProjectV2ItemById": {"item": {"id": "new_item"}}}
        mock_graphql.side_effect = [page1, page2, mutation_result]
        result = _find_or_add_item("P_id", "I_missing")
        self.assertEqual(result, "new_item")
        self.assertEqual(mock_graphql.call_count, 3)

    @patch("project_sync._graphql")
    def test_finds_item_on_first_page_single_call(self, mock_graphql):
        """Issue found on page 1 — only one graphql call, no add."""
        page1 = self._page(
            [self._item("item_found", "I_found")],
            has_next=True,   # more pages exist, but we should stop early
            cursor="cursor_x",
        )
        mock_graphql.return_value = page1
        result = _find_or_add_item("P_id", "I_found")
        self.assertEqual(result, "item_found")
        self.assertEqual(mock_graphql.call_count, 1)

    @patch("project_sync._graphql")
    def test_raises_when_page_info_missing(self, mock_graphql):
        """Response with no pageInfo must raise RuntimeError, not AttributeError."""
        mock_graphql.return_value = {
            "node": {"items": {"nodes": [], "pageInfo": None}}
        }
        with self.assertRaises(RuntimeError):
            _find_or_add_item("P_id", "I_target")


if __name__ == "__main__":
    unittest.main()
