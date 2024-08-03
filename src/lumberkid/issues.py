from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable


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
