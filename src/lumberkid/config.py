from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from lumberkid.git import GitVCS
from lumberkid.github import GithubForge, GithubIssueProvider, parse_issue_title

if TYPE_CHECKING:
    from lumberkid.issues import IssueTitle


@dataclass(frozen=True)
class LumberkidConfig:
    forge: GithubForge = GithubForge(start_as_draft=False, assign_on_add=False, label_on_add=None)  # noqa: RUF009

    issue_source: GithubIssueProvider = GithubIssueProvider()  # noqa: RUF009
    issue_title_parser: Callable[[str], "IssueTitle"] = parse_issue_title
    in_progress_label: str = "in-progress"

    default_branch: str = "main"
    migrate_changes: bool = True

    automerge: bool = True
    squash: bool = True

    vcs: GitVCS = GitVCS()  # noqa: RUF009


def get_config() -> LumberkidConfig:
    """Get the config. In the future, will look for an XDG-compatible .toml"""
    return LumberkidConfig()
