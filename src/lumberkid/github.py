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


@dataclass(frozen=True)
class GithubForge:
    start_as_draft: bool
    assign_on_add: bool
    label_on_add: str | None = ""

    def setup(self) -> Self:
        """Setup. Not using __post_init__ to enable config parsing in tests without requiring gh cli."""
        check_for_gh_cli()
        return self

    @classmethod
    def from_toml(cls: Type["GithubForge"], toml: dict[str, Any]) -> "GithubForge":
        return cls(
            start_as_draft=toml["forge"]["start_as_draft"],  # type: ignore
            assign_on_add=toml["issue_source"]["assign_on_add"],  # type: ignore
            label_on_add=toml["issue_source"]["label_on_add"],  # type: ignore
        )

    def add(self, issue: "Issue"):
        """Issue is not needed for Github, since it infers from the first commit."""
        cmd = f'gh pr create --title "{_pr_title(issue)}" --body ""'
        if self.start_as_draft:
            cmd += " --draft"

        if isinstance(issue, RemoteIssue):
            if self.assign_on_add:
                issue.assign(assignee="@me")
            if self.label_on_add:
                issue.label(self.label_on_add)

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


def _create_label(label: str) -> None:
    shell_output(f"gh label create {label}")


@dataclass(frozen=True)
class GithubIssue(RemoteIssue):
    entity_id: str
    description: str

    def _add_label(self, label: str) -> None:
        if not self.entity_id:
            return

        shell_output(f"gh issue edit {int(self.entity_id)} --add-label {label}")

    def label(self, label: str) -> None:
        if not self.entity_id:
            return

        try:
            self._add_label(label)
        except Exception:
            try:
                _create_label(label)
                self._add_label(label)
            except Exception as e:
                raise RuntimeError(f"Error labeling issue {self.entity_id} with {label}") from e

    def get_comments(self) -> "Sequence[IssueComment]":
        if not self.entity_id:
            return []

        comments_json = shell_output(f"gh issue view {self.entity_id} --json comments")
        comments: Sequence[Mapping[str, str]] = json.loads(comments_json)["comments"]  # type: ignore
        return [_parse_issue_comment(c) for c in comments]

    def assign(self, assignee: str) -> None:
        if not self.entity_id:
            return

        shell_output(f"gh issue edit {int(self.entity_id)} --add-assignee {assignee}")


class GithubIssueProvider:
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

        return cls()

    def _values_to_issue(self, values: dict[str, str]) -> GithubIssue:
        parsed_title = parse_issue_title(values["title"])
        return GithubIssue(
            entity_id=str(values["number"]), title=parsed_title, description=values["body"]
        )

    def get_latest(self, filter_on_label: str) -> "Sequence[GithubIssue]":
        latest_issues = shell_output(
            f"gh issue list --limit 10 --json number,title,body --search 'is:open -label:{filter_on_label}'"
        )

        if latest_issues is None:
            return []

        return self._parse_github_json_str(latest_issues)

    def assigned_to_me(self, filter_on_label: str) -> "Sequence[GithubIssue]":
        """Get issues assigned to current user on current repo"""
        my_issues_cmd = shell_output(
            f"gh issue list --assignee @me  --search '-label:{filter_on_label}' --json number,title,body"
        )

        if my_issues_cmd is None:
            return []

        return self._parse_github_json_str(my_issues_cmd)

    def _parse_github_json_str(self, issue_str: str) -> "Sequence[GithubIssue]":
        values = json.loads(issue_str)
        parsed_output = [self._values_to_issue(v) for v in values]
        return parsed_output
