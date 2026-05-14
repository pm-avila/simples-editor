"""Tests for update_progress.py — sprint PROGRESS.md generator."""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import io
import json
import urllib.error

from update_progress import (
    is_sprint1_issue,
    is_sprint_issue,
    sprint_number_for_issue,
    render_progress,
    write_progress_if_changed,
    _api_request,
    fetch_sprint_issues,
    fetch_sprint1_issues,
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


class TestIsSprintIssue(unittest.TestCase):

    def test_sprint1_label_qualifies(self):
        issue = _make_issue(1, 'bootstrap docs', labels=['sprint-1', 'docs'])
        self.assertTrue(is_sprint1_issue(issue))
        self.assertTrue(is_sprint_issue(issue))
        self.assertEqual(sprint_number_for_issue(issue), 1)

    def test_sprint1_milestone_qualifies(self):
        issue = _make_issue(2, 'setup infra', labels=[])
        issue['milestone'] = {'title': 'Sprint 1'}
        self.assertTrue(is_sprint1_issue(issue))
        self.assertTrue(is_sprint_issue(issue))
        self.assertEqual(sprint_number_for_issue(issue), 1)

    def test_sprint2_label_qualifies(self):
        issue = _make_issue(10, 'editor shell', labels=['sprint-2'])
        self.assertFalse(is_sprint1_issue(issue))
        self.assertTrue(is_sprint_issue(issue))
        self.assertEqual(sprint_number_for_issue(issue), 2)

    def test_sprint2_milestone_qualifies(self):
        issue = _make_issue(11, 'language registration', labels=[])
        issue['milestone'] = {'title': 'Sprint 2'}
        self.assertFalse(is_sprint1_issue(issue))
        self.assertTrue(is_sprint_issue(issue))
        self.assertEqual(sprint_number_for_issue(issue), 2)

    def test_sprint2_label_excluded_from_sprint1_helper(self):
        issue = _make_issue(10, 'sprint 2 work', labels=['sprint-2'])
        self.assertFalse(is_sprint1_issue(issue))

    def test_no_sprint_label_excluded(self):
        issue = _make_issue(5, 'unrelated', labels=['bug'])
        self.assertFalse(is_sprint1_issue(issue))
        self.assertFalse(is_sprint_issue(issue))
        self.assertIsNone(sprint_number_for_issue(issue))

    def test_pull_request_excluded(self):
        issue = _make_issue(3, 'some PR', labels=['sprint-1'], is_pr=True)
        self.assertFalse(is_sprint1_issue(issue))
        self.assertFalse(is_sprint_issue(issue))
        self.assertIsNone(sprint_number_for_issue(issue))

    def test_no_labels_no_milestone_excluded(self):
        issue = _make_issue(7, 'bare issue')
        self.assertFalse(is_sprint1_issue(issue))
        self.assertFalse(is_sprint_issue(issue))
        self.assertIsNone(sprint_number_for_issue(issue))


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

    def _sprint2_issues(self):
        return [
            _make_issue(10, 'feat(editor): integrate Monaco on the main route',
                        state='closed', labels=['sprint-2', 'frontend']),
            _make_issue(11, 'feat(editor): register the SIMPLES Monaco language',
                        state='closed', labels=['sprint-2', 'frontend']),
            _make_issue(12, 'feat(editor): apply dark theme for SIMPLES syntax',
                        state='closed', labels=['sprint-2', 'frontend']),
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

    def test_groups_multiple_sprints_in_order(self):
        issues = [
            _make_issue(10, 'feat(editor): integrate Monaco on the main route',
                        state='closed', labels=['sprint-2', 'frontend']),
            _make_issue(1, 'feat(repo): bootstrap repository documentation',
                        state='closed', labels=['sprint-1', 'docs']),
        ]
        md = render_progress(issues)
        self.assertIn('## Sprint 1\n', md)
        self.assertIn('## Sprint 2\n', md)
        self.assertLess(md.index('## Sprint 1'), md.index('## Sprint 2'))
        self.assertIn('- [x] #1 feat(repo): bootstrap repository documentation', md)
        self.assertIn('- [x] #10 feat(editor): integrate Monaco on the main route', md)

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


def _fake_urlopen_returning(payload):
    """Return a mock context manager whose .read() yields *payload* as JSON bytes."""
    raw = json.dumps(payload).encode()
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=cm)
    cm.__exit__ = MagicMock(return_value=False)
    cm.read = MagicMock(return_value=raw)
    return cm


class TestApiRequest(unittest.TestCase):

    def test_returns_parsed_json_on_success(self):
        payload = [{'id': 1, 'title': 'bootstrap'}]
        with patch('urllib.request.urlopen', return_value=_fake_urlopen_returning(payload)):
            result = _api_request('https://api.github.com/repos/x/y/issues', 'tok')
        self.assertEqual(result, payload)

    def test_raises_runtime_error_on_http_error(self):
        err = urllib.error.HTTPError(
            url='https://api.github.com/repos/x/y/issues',
            code=403,
            msg='Forbidden',
            hdrs={},
            fp=io.BytesIO(b'rate limit exceeded'),
        )
        with patch('urllib.request.urlopen', side_effect=err):
            with self.assertRaises(RuntimeError) as ctx:
                _api_request('https://api.github.com/repos/x/y/issues', 'tok')
        self.assertIn('403', str(ctx.exception))

    def test_sets_authorization_header(self):
        payload = []
        captured = {}

        def fake_urlopen(req):
            captured['headers'] = req.headers
            return _fake_urlopen_returning(payload)

        with patch('urllib.request.urlopen', side_effect=fake_urlopen):
            _api_request('https://api.github.com/repos/x/y/issues', 'mytoken')

        self.assertIn('Authorization', captured['headers'])
        self.assertIn('mytoken', captured['headers']['Authorization'])


def _sprint1_item(number, title='item', state='open'):
    return {
        'number': number,
        'title': title,
        'state': state,
        'labels': [{'name': 'sprint-1'}],
        'milestone': None,
    }


def _sprint2_item(number, title='item', state='open'):
    return {
        'number': number,
        'title': title,
        'state': state,
        'labels': [{'name': 'sprint-2'}],
        'milestone': None,
    }


class TestFetchSprint1Issues(unittest.TestCase):

    def test_returns_sprint1_issues_from_single_page(self):
        items = [_sprint1_item(1), _sprint1_item(2)]
        with patch('update_progress._api_request', return_value=items):
            result = fetch_sprint1_issues('tok', 'owner/repo')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['number'], 1)

    def test_paginates_until_short_page(self):
        page1 = [_sprint1_item(i) for i in range(1, 101)]   # 100 items → continue
        page2 = [_sprint1_item(i) for i in range(101, 106)]  # 5 items → stop
        pages = iter([page1, page2])
        with patch('update_progress._api_request', side_effect=lambda url, tok: next(pages)):
            result = fetch_sprint1_issues('tok', 'owner/repo')
        self.assertEqual(len(result), 105)

    def test_stops_on_empty_page(self):
        with patch('update_progress._api_request', return_value=[]):
            result = fetch_sprint1_issues('tok', 'owner/repo')
        self.assertEqual(result, [])

    def test_filters_out_non_sprint1_items(self):
        items = [
            _sprint1_item(1),
            {'number': 2, 'title': 'sprint-2 work', 'state': 'open',
             'labels': [{'name': 'sprint-2'}], 'milestone': None},
        ]
        with patch('update_progress._api_request', return_value=items):
            result = fetch_sprint1_issues('tok', 'owner/repo')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['number'], 1)

    def test_filters_out_pull_requests(self):
        pr = {**_sprint1_item(3), 'pull_request': {'url': 'https://api.github.com/repos/x/y/pulls/3'}}
        items = [_sprint1_item(1), pr]
        with patch('update_progress._api_request', return_value=items):
            result = fetch_sprint1_issues('tok', 'owner/repo')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['number'], 1)

    def test_propagates_api_error(self):
        with patch('update_progress._api_request', side_effect=RuntimeError('API 403')):
            with self.assertRaises(RuntimeError):
                fetch_sprint1_issues('tok', 'owner/repo')

    def test_url_includes_page_number(self):
        page1 = [_sprint1_item(i) for i in range(1, 101)]
        page2 = [_sprint1_item(101)]
        calls = []

        def fake_api(url, tok):
            calls.append(url)
            return page1 if url.endswith('page=1') else page2

        with patch('update_progress._api_request', side_effect=fake_api):
            fetch_sprint1_issues('tok', 'owner/repo')

        self.assertTrue(any('page=1' in u for u in calls), 'page=1 not requested')
        self.assertTrue(any('page=2' in u for u in calls), 'page=2 not requested')


class TestFetchSprintIssues(unittest.TestCase):

    def test_returns_sprint1_and_sprint2_issues_from_single_page(self):
        items = [_sprint1_item(1), _sprint2_item(10)]
        with patch('update_progress._api_request', return_value=items):
            result = fetch_sprint_issues('tok', 'owner/repo')
        self.assertEqual([item['number'] for item in result], [1, 10])

    def test_filters_out_non_sprint_items(self):
        items = [
            _sprint1_item(1),
            {'number': 2, 'title': 'docs', 'state': 'open',
             'labels': [{'name': 'docs'}], 'milestone': None},
        ]
        with patch('update_progress._api_request', return_value=items):
            result = fetch_sprint_issues('tok', 'owner/repo')
        self.assertEqual([item['number'] for item in result], [1])


class TestProgressSyncWorkflowPermissions(unittest.TestCase):
    """Workflow file must declare the permissions needed by update_progress.py."""

    _WORKFLOW_PATH = os.path.join(
        os.path.dirname(__file__), '..', '.github', 'workflows', 'progress-sync.yml'
    )

    def _workflow_text(self):
        with open(self._WORKFLOW_PATH, encoding='utf-8') as fh:
            return fh.read()

    def test_workflow_declares_issues_read_permission(self):
        """update_progress.py calls the Issues REST API so the workflow needs issues: read."""
        text = self._workflow_text()
        self.assertIn('issues: read', text,
                      'progress-sync.yml must include "issues: read" under permissions')


if __name__ == '__main__':
    unittest.main()
