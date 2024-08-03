import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

from lumberkid.issue_provider.issues import Issue, IssueTitle
from lumberkid.subprocess_utils import interactive_cmd, shell_output

if TYPE_CHECKING:
    from collections.abc import Sequence


import shutil


def cli_tool_exists(tool_name: str) -> bool:
    return shutil.which(tool_name) is not None


def check_for_gh_cli():
    if not cli_tool_exists("gh"):
        raise RuntimeError("GitHub CLI not found on your path at `gh`. Please install it.")


@dataclass
class IssueComment:
    id: str
    author_login: str
    body: str
    url: str


def _parse_issue_comment(comment_json: Mapping[str, str]) -> IssueComment:
    return IssueComment(
        id=comment_json["id"],  # type: ignore
        body=comment_json["body"],  # type: ignore
        url=comment_json["url"],  # type: ignore
        author_login=comment_json["author"]["login"],  # type: ignore
    )


def _pr_title(issue: "Issue") -> str:
    pr_title = f"{issue.title.prefix}: " if issue.title.prefix else ""
    pr_title += issue.title.content

    return pr_title


def parse_issue_title(issue_title: str) -> IssueTitle:
    # Get all string between start and first ":"
    try:
        prefix = re.findall(r"^(.*?)[\(:]", issue_title)[0]
    except IndexError:
        # No prefix found, return without prefix
        return IssueTitle(prefix=None, content=issue_title)

    description = re.findall(r": (.*)$", issue_title)[0]
    return IssueTitle(prefix=prefix, content=description)


def setup():
    """Setup. Not using __post_init__ to enable config parsing in tests without requiring gh cli."""
    check_for_gh_cli()


def begin(issue: "Issue", start_as_draft: bool):
    """Issue is not needed for Github, since it infers from the first commit."""
    cmd = f'gh pr create --title "{_pr_title(issue)}" --body ""'
    if start_as_draft:
        cmd += " --draft"

    interactive_cmd(cmd)


def merge(automerge: bool, squash: bool, mark_as_ready: bool):
    if mark_as_ready:
        interactive_cmd("gh pr ready")

    merge_cmd = "gh pr merge"
    if automerge:
        merge_cmd += " --auto"
    if squash:
        merge_cmd += " --squash"

    interactive_cmd(merge_cmd)


def get_comments(issue_id: str) -> "Sequence[IssueComment]":
    comments_json = shell_output(f"gh issue view {issue_id} --json comments")
    comments: Sequence[Mapping[str, str]] = json.loads(comments_json)["comments"]  # type: ignore
    return [_parse_issue_comment(c) for c in comments]
