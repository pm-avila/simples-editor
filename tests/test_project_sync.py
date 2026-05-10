"""Tests for project_sync.py - Sprint 1 kanban automation core."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from project_sync import is_sprint1_eligible, determine_status, _get_linked_pr


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

    def test_in_review_pr_without_draft_key_treated_as_ready(self):
        """PR dict with no 'draft' key is treated as non-draft (In review)."""
        pr_without_draft = {"state": "open"}
        self.assertEqual(
            determine_status(self._open_issue(), pr=pr_without_draft), "In review"
        )

    def test_done_closed_issue(self):
        self.assertEqual(determine_status(self._closed_issue(), pr=None), "Done")

    def test_done_closed_issue_ignores_pr(self):
        """Closed issue is Done regardless of PR state."""
        self.assertEqual(
            determine_status(self._closed_issue(), pr=self._ready_pr()), "Done"
        )


class TestLinkedPrMatching(unittest.TestCase):
    """Unit tests for the PR number matching logic inside _get_linked_pr.

    We test the regex pattern directly (extracted from the function) to
    avoid making real HTTP calls.
    """

    import re as _re

    def _pr(self, body="", title="", draft=False):
        return {"state": "open", "draft": draft, "body": body, "title": title}

    def _matches(self, issue_number, pr):
        import re
        pattern = re.compile(r"#" + re.escape(str(issue_number)) + r"(?!\d)")
        return bool(
            pattern.search(pr.get("body") or "")
            or pattern.search(pr.get("title") or "")
        )

    def test_matches_exact_issue_reference_in_body(self):
        pr = self._pr(body="Closes #12.")
        self.assertTrue(self._matches(12, pr))

    def test_matches_exact_issue_reference_in_title(self):
        pr = self._pr(title="fix: resolve #12")
        self.assertTrue(self._matches(12, pr))

    def test_no_false_positive_superstring_number(self):
        """#12 must NOT match a PR that only mentions #123."""
        pr = self._pr(body="Closes #123")
        self.assertFalse(self._matches(12, pr))

    def test_no_false_positive_prefix_number(self):
        """#12 must NOT match a PR that only mentions #1234."""
        pr = self._pr(body="see #1234 for context")
        self.assertFalse(self._matches(12, pr))

    def test_no_match_when_pr_unrelated(self):
        pr = self._pr(body="Fixes a typo in README", title="chore: cleanup")
        self.assertFalse(self._matches(12, pr))


if __name__ == "__main__":
    unittest.main()
