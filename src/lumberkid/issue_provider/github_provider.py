import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from lumberkid.forge.github_forge import check_for_gh_cli, parse_issue_title
from lumberkid.issue_provider.issues import RemoteIssue
from lumberkid.subprocess_utils import shell_output

if TYPE_CHECKING:
    from lumberkid.issue_provider.issues import Issue


@dataclass(frozen=True)
class GithubIssue(RemoteIssue):
    entity_id: str
    description: str


def _parse_github_json_str(issue_str: str) -> "Sequence[GithubIssue]":
    values = json.loads(issue_str)
    parsed_output = [_values_to_issue(v) for v in values]
    return parsed_output


def _values_to_issue(values: dict[str, str]) -> GithubIssue:
    parsed_title = parse_issue_title(values["title"])
    return GithubIssue(
        entity_id=str(values["number"]), title=parsed_title, description=values["body"]
    )


def _create_label(label: str) -> None:
    shell_output(f"gh label create {label}")


def _add_label(label: str, issue_id: str) -> None:
    shell_output(f"gh issue edit {int(issue_id)} --add-label {label}")


def _label(label: str, issue_id: str) -> None:
    if not issue_id:
        return

    try:
        _add_label(label, issue_id)
    except Exception:
        try:
            _create_label(label)
            _add_label(label, issue_id)
        except Exception as e:
            raise RuntimeError(f"Error labeling issue {issue_id} with {label}") from e


def _assign(assignee: str, issue_id: str) -> None:
    shell_output(f"gh issue edit {int(issue_id)} --add-assignee {assignee}")


def setup():
    """Setup. Not using __post_init__ to enable config parsing in tests without requiring gh cli."""
    check_for_gh_cli()


def begin(issue: "Issue", assign_on_begin: str, label_on_begin: str):
    """Issue is not needed for Github, since it infers from the first commit."""
    if isinstance(issue, RemoteIssue):
        if assign_on_begin:
            _assign(assignee=assign_on_begin, issue_id=issue.entity_id)
        if label_on_begin:
            _label(label_on_begin, issue_id=issue.entity_id)


def get_latest(filter_on_label: str) -> "Sequence[GithubIssue]":
    latest_issues = shell_output(
        f"gh issue list --limit 10 --json number,title,body --search 'is:open -label:{filter_on_label}'"
    )

    if latest_issues is None:
        return []

    return _parse_github_json_str(latest_issues)


def assigned_to_me(filter_on_label: str) -> "Sequence[GithubIssue]":
    """Get issues assigned to current user on current repo"""
    my_issues_cmd = shell_output(
        f"gh issue list --assignee @me  --search '-label:{filter_on_label}' --json number,title,body"
    )

    if my_issues_cmd is None:
        return []

    return _parse_github_json_str(my_issues_cmd)
