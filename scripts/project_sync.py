"""
project_sync.py — GitHub Project kanban sync core.

Orchestrates status updates for issues in pm-avila's Project 2.
Uses Python stdlib only (urllib, json, os).
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error


# ---------------------------------------------------------------------------
# Sprint 1 eligibility
# ---------------------------------------------------------------------------

def is_sprint1_eligible(issue: dict) -> bool:
    """Return True if the issue belongs to Sprint 1 (milestone or label)."""
    milestone = issue.get("milestone") or {}
    if milestone.get("title") == "Sprint 1":
        return True
    for label in issue.get("labels", []):
        if label.get("name") == "sprint-1":
            return True
    return False


# ---------------------------------------------------------------------------
# Status mapping
# ---------------------------------------------------------------------------

def determine_status(issue: dict, pr: dict | None = None) -> str:
    """
    Map issue + PR state to a Project Status option name.

    Rules:
      - closed issue                    → Done
      - open issue, ready (non-draft) PR → In review
      - open issue, draft PR            → In progress
      - open issue, no PR               → Backlog
    """
    if issue.get("state") == "closed":
        return "Done"
    if pr is not None:
        if "draft" not in pr:
            raise RuntimeError(
                "PR payload is missing 'draft' field — malformed API response"
            )
        if pr["draft"]:
            return "In progress"
        return "In review"
    return "Backlog"


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def _gh_token() -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN or GITHUB_TOKEN environment variable must be set")
    return token


def _api_request(method: str, url: str, body: dict | None = None) -> dict:
    token = _gh_token()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        raise RuntimeError(
            f"GitHub API {method} {url} returned {exc.code}: {body_text}"
        ) from exc


def _graphql(query: str, variables: dict | None = None) -> dict:
    token = _gh_token()
    payload = {"query": query, "variables": variables or {}}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        raise RuntimeError(f"GraphQL request failed {exc.code}: {body_text}") from exc

    if "errors" in result:
        raise RuntimeError(f"GraphQL errors: {result['errors']}")
    if "data" not in result:
        raise RuntimeError(
            f"GraphQL response missing 'data' key — unexpected response shape: {result!r}"
        )
    return result["data"]


# ---------------------------------------------------------------------------
# Project orchestration
# ---------------------------------------------------------------------------

PROJECT_OWNER = "pm-avila"
PROJECT_NUMBER = 2

_GET_PROJECT_Q = """
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      id
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options { id name }
          }
        }
      }
    }
  }
}
"""

_ADD_ITEM_Q = """
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
    item { id }
  }
}
"""

_UPDATE_FIELD_Q = """
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId,
    itemId: $itemId,
    fieldId: $fieldId,
    value: { singleSelectOptionId: $optionId }
  }) {
    projectV2Item { id }
  }
}
"""

_GET_ITEM_Q = """
query($projectId: ID!, $after: String) {
  node(id: $projectId) {
    ... on ProjectV2 {
      items(first: 100, after: $after) {
        nodes {
          id
          content { ... on Issue { id } }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""


def _get_project_meta() -> tuple[str, str, dict[str, str]]:
    """Return (project_id, status_field_id, {option_name: option_id})."""
    data = _graphql(_GET_PROJECT_Q, {"owner": PROJECT_OWNER, "number": PROJECT_NUMBER})
    user = data.get("user")
    if user is None:
        raise RuntimeError(
            f"GraphQL response has no 'user' data — check PROJECT_OWNER ({PROJECT_OWNER!r})"
        )
    project = user.get("projectV2")
    if project is None:
        raise RuntimeError(
            f"Project {PROJECT_NUMBER} not found for user {PROJECT_OWNER!r} "
            "— verify PROJECT_NUMBER and repository ownership"
        )
    project_id = project.get("id")
    if not project_id:
        raise RuntimeError(
            "GraphQL projectV2 response missing 'id' — unexpected API response shape"
        )

    fields = project.get("fields")
    if fields is None:
        raise RuntimeError(
            "GraphQL response has no 'fields' on project — unexpected API response shape"
        )
    nodes = fields.get("nodes")
    if nodes is None:
        raise RuntimeError(
            "GraphQL project 'fields' has no 'nodes' — unexpected API response shape"
        )

    status_field = None
    for field in nodes:
        if field.get("name") == "Status":
            status_field = field
            break
    if status_field is None:
        raise RuntimeError("Status field not found in project")

    options_list = status_field.get("options")
    if options_list is None:
        raise RuntimeError(
            "Status field has no 'options' key — unexpected field shape in API response"
        )
    options = {}
    for opt in options_list:
        opt_name = opt.get("name")
        opt_id = opt.get("id")
        if opt_name is None or opt_id is None:
            raise RuntimeError(
                f"Status field option missing 'name' or 'id' — unexpected API response shape: {opt!r}"
            )
        options[opt_name] = opt_id
    field_id = status_field.get("id")
    if not field_id:
        raise RuntimeError(
            "Status field missing 'id' — unexpected API response shape"
        )
    return project_id, field_id, options


def _find_or_add_item(project_id: str, issue_node_id: str) -> str:
    """Return the project item ID for the issue, adding it if absent."""
    cursor = None
    while True:
        data = _graphql(_GET_ITEM_Q, {"projectId": project_id, "after": cursor})
        node = data.get("node")
        if node is None:
            raise RuntimeError(
                f"GraphQL 'node' is null — project id {project_id!r} not found or not accessible"
            )
        items_wrap = node.get("items")
        if items_wrap is None:
            raise RuntimeError(
                "GraphQL node has no 'items' — unexpected API response shape"
            )
        item_nodes = items_wrap.get("nodes")
        if item_nodes is None:
            raise RuntimeError(
                "GraphQL items has no 'nodes' — unexpected API response shape"
            )
        for item in item_nodes:
            content = item.get("content") or {}
            if content.get("id") == issue_node_id:
                item_id = item.get("id")
                if not item_id:
                    raise RuntimeError(
                        f"Project item matched issue but has no 'id' — unexpected API response shape: {item!r}"
                    )
                return item_id

        page_info = items_wrap.get("pageInfo")
        if page_info is None:
            raise RuntimeError(
                "GraphQL items has no 'pageInfo' — unexpected API response shape"
            )
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            raise RuntimeError(
                "GraphQL pageInfo has hasNextPage=true but endCursor is null/empty "
                "— unexpected API response shape"
            )

    added = _graphql(_ADD_ITEM_Q, {"projectId": project_id, "contentId": issue_node_id})
    mutation_result = added.get("addProjectV2ItemById")
    if mutation_result is None:
        raise RuntimeError(
            "addProjectV2ItemById returned null — item was not added to the project "
            "(check project permissions and issue node id)"
        )
    item = mutation_result.get("item")
    if item is None:
        raise RuntimeError(
            "addProjectV2ItemById returned null item — item was not created "
            "(check project permissions and issue node id)"
        )
    item_id = item.get("id")
    if not item_id:
        raise RuntimeError(
            "addProjectV2ItemById returned item with no 'id' — unexpected API response shape"
        )
    return item_id


def _update_status(
    project_id: str, item_id: str, field_id: str, option_id: str
) -> None:
    _graphql(
        _UPDATE_FIELD_Q,
        {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "optionId": option_id,
        },
    )


# ---------------------------------------------------------------------------
# Event parsing
# ---------------------------------------------------------------------------

# All GitHub close keywords (singular, plural, past tense).
# https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue
_CLOSE_KW_RE = re.compile(
    r"(?:clos(?:e|es|ed)|fix(?:es|ed)?|resolv(?:e|es|ed))\s+#(\d+)",
    re.IGNORECASE,
)


def _load_event() -> dict:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        raise RuntimeError("GITHUB_EVENT_PATH environment variable must be set")
    if not os.path.exists(path):
        raise RuntimeError(f"Event file not found: {path}")
    with open(path) as f:
        return json.load(f)


def _extract_linked_issue_number(pr: dict) -> int:
    """Parse the first GitHub close-keyword #N reference from the PR body.

    Recognises all supported variants: close/closes/closed, fix/fixes/fixed,
    resolve/resolves/resolved (case-insensitive).

    Raises RuntimeError if the PR body contains no recognised linked-issue
    reference, since that makes it impossible to determine issue context for
    a pull_request event.
    """
    body = pr.get("body") or ""
    match = _CLOSE_KW_RE.search(body)
    if not match:
        raise RuntimeError(
            "pull_request payload has no linked issue reference "
            "(expected a GitHub close keyword followed by #N in PR body, "
            "e.g. 'Closes #42', 'Fixed #7', 'Resolved #100')"
        )
    return int(match.group(1))


def _fetch_issue(issue_number: int, repo: str) -> dict:
    """Fetch a single issue by number from the GitHub REST API."""
    parts = repo.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise RuntimeError(
            f"GITHUB_REPOSITORY must be in 'owner/repo' format, got: {repo!r}"
        )
    owner, name = parts
    url = f"https://api.github.com/repos/{owner}/{name}/issues/{issue_number}"
    return _api_request("GET", url)


def _fetch_linked_pr_for_issue(issue_number: int, repo: str) -> dict | None:
    """Return the first open PR in *repo* whose body references *issue_number*, or None.

    Searches open PRs for a Closes/Fixes/Resolves #N reference matching
    *issue_number*.  Returns the full PR dict (which includes the 'draft' field)
    so callers can pass it straight to determine_status().
    """
    parts = repo.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise RuntimeError(
            f"GITHUB_REPOSITORY must be in 'owner/repo' format, got: {repo!r}"
        )
    owner, name = parts
    url = f"https://api.github.com/repos/{owner}/{name}/pulls?state=open&per_page=100"
    prs = _api_request("GET", url)
    for pr in prs:
        body = pr.get("body") or ""
        for match in _CLOSE_KW_RE.finditer(body):
            if int(match.group(1)) == issue_number:
                return pr
    return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run() -> None:
    event = _load_event()

    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        raise RuntimeError("GITHUB_REPOSITORY environment variable must be set")

    if "issue" in event:
        issue = event["issue"]
        pr = None
    elif "pull_request" in event:
        pr = event["pull_request"]
        issue_number = _extract_linked_issue_number(pr)
        issue = _fetch_issue(issue_number, repo)
    else:
        raise RuntimeError(
            "Event payload has neither 'issue' nor 'pull_request' key; "
            "unsupported event type"
        )

    if not is_sprint1_eligible(issue):
        print(
            f"Issue #{issue['number']} is not Sprint 1 eligible — skipping.",
            file=sys.stderr,
        )
        return

    # For issue events on open Sprint-1 issues, check for an active linked PR
    # so we never regress status from In progress/In review back to Backlog.
    if "issue" in event and issue.get("state") != "closed":
        pr = _fetch_linked_pr_for_issue(issue["number"], repo)

    status = determine_status(issue, pr)

    project_id, field_id, options = _get_project_meta()

    if status not in options:
        raise RuntimeError(
            f"Status '{status}' not found in project options: {list(options)}"
        )

    issue_node_id = issue.get("node_id")
    if not issue_node_id:
        raise RuntimeError(
            f"Issue #{issue.get('number')} payload is missing 'node_id' "
            "— unexpected API response shape"
        )
    item_id = _find_or_add_item(project_id, issue_node_id)
    _update_status(project_id, item_id, field_id, options[status])

    print(f"Issue #{issue['number']} → Status: {status}")


if __name__ == "__main__":
    run()
