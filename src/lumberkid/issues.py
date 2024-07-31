from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence

    from lumberkid.github import IssueComment


@dataclass(frozen=True)
class IssueTitle:
    prefix: Optional[str]
    content: str

    def __str__(self) -> str:
        if self.prefix:
            return f"{self.prefix}: {self.content}"
        return f"{self.content}"


@runtime_checkable
class Issue(Protocol):
    title: IssueTitle


@dataclass(frozen=True)
class LocalIssue(Issue):
    """Issue created by entering a title in the CLI"""

    title: IssueTitle


@dataclass(frozen=True)
class RemoteIssue(Issue):
    """Issue created by a remote source (e.g. Github)"""

    title: IssueTitle
    entity_id: str
    description: str

    def label(self, label: str) -> None:
        ...

    def assign(self, assignee: str) -> None:
        ...

    def get_comments(self) -> "Sequence[IssueComment]":
        ...
