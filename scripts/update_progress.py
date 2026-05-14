"""
update_progress.py — Generate PROGRESS.md from sprint GitHub issues.

Fetches issues from GitHub REST API (Python stdlib only) and renders a
markdown checklist sorted by issue number.  Only real issues are included
(pull requests are excluded via the `pull_request` field).
"""

import json
import os
import sys
import urllib.error
import urllib.request


# ---------------------------------------------------------------------------
# Sprint eligibility
# ---------------------------------------------------------------------------

def sprint_number_for_issue(issue: dict):
    """Return the sprint number for *issue*, or None if it is not a sprint issue."""
    if 'pull_request' in issue:
        return None
    milestone = issue.get('milestone') or {}
    title = milestone.get('title', '')
    if title.startswith('Sprint '):
        try:
            return int(title.split(' ', 1)[1])
        except (IndexError, ValueError):
            pass
    for label in issue.get('labels', []):
        name = label.get('name') if isinstance(label, dict) else label
        if name and name.startswith('sprint-'):
            try:
                return int(name.split('-', 1)[1])
            except (IndexError, ValueError):
                pass
    return None


def is_sprint_issue(issue: dict) -> bool:
    """Return True if *issue* belongs to any sprint and is not a pull request."""
    return sprint_number_for_issue(issue) is not None


def is_sprint1_issue(issue: dict) -> bool:
    """Return True if *issue* belongs to Sprint 1 and is not a pull request."""
    return sprint_number_for_issue(issue) == 1


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

def render_progress(issues: list) -> str:
    """Render a PROGRESS.md string from a list of issue dicts."""
    grouped = {}
    for issue in issues:
        sprint_number = sprint_number_for_issue(issue)
        if sprint_number is None:
            continue
        grouped.setdefault(sprint_number, []).append(issue)

    lines = ['# Progress', '']
    if not grouped:
        lines.extend(['## Sprint 1', ''])
        return '\n'.join(lines)

    for sprint_number in sorted(grouped):
        lines.extend([f'## Sprint {sprint_number}', ''])
        for issue in sorted(grouped[sprint_number], key=lambda i: i['number']):
            state = issue.get('state', 'open')
            box = 'x' if state == 'closed' else ' '
            lines.append(f"- [{box}] #{issue['number']} {issue['title']}")
        lines.append('')
    lines.append('')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def write_progress_if_changed(path: str, content: str) -> bool:
    """Write *content* to *path* only if it differs from the current file.

    Returns True when the file was written (new or changed), False otherwise.
    """
    try:
        with open(path, encoding='utf-8') as fh:
            current = fh.read()
    except FileNotFoundError:
        current = None
    if current == content:
        return False
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(content)
    return True


# ---------------------------------------------------------------------------
# GitHub REST API helpers
# ---------------------------------------------------------------------------

def _api_request(url: str, token: str) -> object:
    """Perform a GET request against the GitHub REST API and return parsed JSON."""
    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': 'update-progress/1.0',
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors='replace')
        raise RuntimeError(f'GitHub API error {exc.code} for {url}: {body}') from exc


def fetch_sprint_issues(token: str, repo: str) -> list:
    """Fetch all sprint issues from *repo* (owner/name) via the REST API."""
    issues = []
    page = 1
    while True:
        url = (
            f'https://api.github.com/repos/{repo}/issues'
            f'?state=all&per_page=100&page={page}'
        )
        page_data = _api_request(url, token)
        if not page_data:
            break
        for item in page_data:
            if is_sprint_issue(item):
                issues.append(item)
        if len(page_data) < 100:
            break
        page += 1
    return issues


def fetch_sprint1_issues(token: str, repo: str) -> list:
    """Fetch only Sprint 1 issues from *repo* (owner/name) via the REST API."""
    return [
        issue
        for issue in fetch_sprint_issues(token, repo)
        if sprint_number_for_issue(issue) == 1
    ]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    token = os.environ.get('GITHUB_TOKEN', '')
    repo = os.environ.get('GITHUB_REPOSITORY', 'pm-avila/simples-editor')
    output_path = os.path.join(
        os.path.dirname(__file__), '..', 'PROGRESS.md'
    )

    if not token:
        sys.exit('GITHUB_TOKEN environment variable is required')

    print(f'Fetching sprint issues from {repo}…', file=sys.stderr)
    issues = fetch_sprint_issues(token, repo)
    print(f'Found {len(issues)} sprint issues.', file=sys.stderr)

    content = render_progress(issues)
    changed = write_progress_if_changed(output_path, content)
    if changed:
        print('PROGRESS.md updated.', file=sys.stderr)
    else:
        print('PROGRESS.md unchanged.', file=sys.stderr)


if __name__ == '__main__':
    main()
