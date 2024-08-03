import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping, Self, Type

from lumberkid.issues import Issue, IssueTitle, RemoteIssue
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


def _create_label(label: str) -> None:
    shell_output(f"gh label create {label}")


@dataclass(frozen=True)
class GithubForge:
    start_as_draft: bool

    def setup(self) -> Self:
        """Setup. Not using __post_init__ to enable config parsing in tests without requiring gh cli."""
        check_for_gh_cli()
        return self

    @classmethod
    def from_toml(cls: Type["GithubForge"], toml: dict[str, Any]) -> "GithubForge":
        return cls(start_as_draft=toml["forge"]["start_as_draft"])

    def begin(self, issue: "Issue"):
        """Issue is not needed for Github, since it infers from the first commit."""
        cmd = f'gh pr create --title "{_pr_title(issue)}" --body ""'
        if self.start_as_draft:
            cmd += " --draft"

        interactive_cmd(cmd)

    def merge(self, automerge: bool, squash: bool):
        if self.start_as_draft:
            interactive_cmd("gh pr ready")

        merge_cmd = "gh pr merge"
        if automerge:
            merge_cmd += " --auto"
        if squash:
            merge_cmd += " --squash"

        interactive_cmd(merge_cmd)


def _add_label(label: str, issue_id: str) -> None:
    shell_output(f"gh issue edit {int(issue_id)} --add-label {label}")


def get_comments(issue_id: str) -> "Sequence[IssueComment]":
    comments_json = shell_output(f"gh issue view {issue_id} --json comments")
    comments: Sequence[Mapping[str, str]] = json.loads(comments_json)["comments"]  # type: ignore
    return [_parse_issue_comment(c) for c in comments]


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


@dataclass(frozen=True)
class GithubIssueProvider:
    assign_on_begin: str = ""
    label_on_begin: str = ""

    def setup(self) -> Self:
        """Setup. Not using __post_init__ to enable config parsing in tests without requiring gh cli."""
        check_for_gh_cli()
        return self

    @classmethod
    def from_toml(
        cls: Type["GithubIssueProvider"], toml: dict[str, Any] | None
    ) -> "GithubIssueProvider":
        if toml is None:
            return cls()

        return cls(assign_on_begin=toml["assign_on_begin"], label_on_begin=toml["label_on_begin"])

    def begin(self, issue: "Issue"):
        """Issue is not needed for Github, since it infers from the first commit."""
        if isinstance(issue, RemoteIssue):
            if self.assign_on_begin:
                self.assign(assignee=self.assign_on_begin, issue_id=issue.entity_id)
            if self.label_on_begin:
                self.label(self.label_on_begin, issue_id=issue.entity_id)

    def get_latest(self, filter_on_label: str) -> "Sequence[GithubIssue]":
        latest_issues = shell_output(
            f"gh issue list --limit 10 --json number,title,body --search 'is:open -label:{filter_on_label}'"
        )

        if latest_issues is None:
            return []

        return _parse_github_json_str(latest_issues)

    def assigned_to_me(self, filter_on_label: str) -> "Sequence[GithubIssue]":
        """Get issues assigned to current user on current repo"""
        my_issues_cmd = shell_output(
            f"gh issue list --assignee @me  --search '-label:{filter_on_label}' --json number,title,body"
        )

        if my_issues_cmd is None:
            return []

        return _parse_github_json_str(my_issues_cmd)

    def label(self, label: str, issue_id: str) -> None:
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

    def assign(self, assignee: str, issue_id: str) -> None:
        shell_output(f"gh issue edit {int(issue_id)} --add-assignee {assignee}")
