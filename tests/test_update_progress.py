"""Tests for update_progress.py — Sprint 1 PROGRESS.md generator."""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from update_progress import (
    is_sprint1_issue,
    render_progress,
    write_progress_if_changed,
)


def _make_issue(number, title, state='open', labels=None, is_pr=False):
    issue = {
        'number': number,
        'title': title,
        'state': state,
        'labels': [{'name': l} for l in (labels or [])],
    }
    if is_pr:
        issue['pull_request'] = {'url': 'https://api.github.com/repos/x/y/pulls/1'}
    return issue


class TestIsSprint1Issue(unittest.TestCase):

    def test_sprint1_label_qualifies(self):
        issue = _make_issue(1, 'bootstrap docs', labels=['sprint-1', 'docs'])
        self.assertTrue(is_sprint1_issue(issue))

    def test_sprint1_milestone_qualifies(self):
        issue = _make_issue(2, 'setup infra', labels=[])
        issue['milestone'] = {'title': 'Sprint 1'}
        self.assertTrue(is_sprint1_issue(issue))

    def test_sprint2_label_excluded(self):
        issue = _make_issue(10, 'sprint 2 work', labels=['sprint-2'])
        self.assertFalse(is_sprint1_issue(issue))

    def test_no_sprint_label_excluded(self):
        issue = _make_issue(5, 'unrelated', labels=['bug'])
        self.assertFalse(is_sprint1_issue(issue))

    def test_pull_request_excluded(self):
        issue = _make_issue(3, 'some PR', labels=['sprint-1'], is_pr=True)
        self.assertFalse(is_sprint1_issue(issue))

    def test_no_labels_no_milestone_excluded(self):
        issue = _make_issue(7, 'bare issue')
        self.assertFalse(is_sprint1_issue(issue))


class TestRenderProgress(unittest.TestCase):

    def _sprint1_issues(self):
        return [
            _make_issue(1, 'feat(repo): bootstrap repository documentation',
                        state='closed', labels=['sprint-1', 'docs']),
            _make_issue(2, 'feat(project): configure delivery kanban workflow',
                        state='open', labels=['sprint-1', 'devops']),
            _make_issue(3, 'feat(infra): scaffold docker compose foundation',
                        state='open', labels=['sprint-1', 'devops']),
        ]

    def test_output_starts_with_progress_heading(self):
        md = render_progress(self._sprint1_issues())
        self.assertTrue(md.startswith('# Progress\n'))

    def test_sprint1_section_present(self):
        md = render_progress(self._sprint1_issues())
        self.assertIn('## Sprint 1\n', md)

    def test_closed_issue_renders_checked(self):
        md = render_progress(self._sprint1_issues())
        self.assertIn('- [x] #1 feat(repo): bootstrap repository documentation', md)

    def test_open_issue_renders_unchecked(self):
        md = render_progress(self._sprint1_issues())
        self.assertIn('- [ ] #2 feat(project): configure delivery kanban workflow', md)

    def test_entries_sorted_by_number(self):
        issues = list(reversed(self._sprint1_issues()))  # supply in reverse order
        md = render_progress(issues)
        pos1 = md.index('- [x] #1')
        pos2 = md.index('- [ ] #2')
        pos3 = md.index('- [ ] #3')
        self.assertLess(pos1, pos2)
        self.assertLess(pos2, pos3)

    def test_empty_sprint1_shows_section_no_entries(self):
        md = render_progress([])
        self.assertIn('## Sprint 1\n', md)
        self.assertNotIn('- [', md)

    def test_output_stable_for_same_input(self):
        issues = self._sprint1_issues()
        self.assertEqual(render_progress(issues), render_progress(issues))


class TestWriteProgressIfChanged(unittest.TestCase):

    def test_writes_file_when_missing(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'PROGRESS.md')
            changed = write_progress_if_changed(path, '# Progress\n')
            self.assertTrue(changed)
            with open(path) as fh:
                self.assertEqual(fh.read(), '# Progress\n')

    def test_returns_false_when_content_identical(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'PROGRESS.md')
            content = '# Progress\n'
            with open(path, 'w') as fh:
                fh.write(content)
            changed = write_progress_if_changed(path, content)
            self.assertFalse(changed)

    def test_returns_true_when_content_differs(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'PROGRESS.md')
            with open(path, 'w') as fh:
                fh.write('# Progress\n')
            changed = write_progress_if_changed(path, '# Progress\n\n## Sprint 1\n')
            self.assertTrue(changed)


if __name__ == '__main__':
    unittest.main()
