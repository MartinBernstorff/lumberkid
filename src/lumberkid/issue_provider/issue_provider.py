from typing import TYPE_CHECKING, Literal, Protocol, Sequence

import pydantic

if TYPE_CHECKING:
    from lumberkid.issue_provider.github_provider import GithubIssue
    from lumberkid.issue_provider.issues import Issue


class IssueProviderConfig(pydantic.BaseModel):
    provider: Literal["github"] = "github"
    assign_on_begin: str = ""
    label_on_begin: str = ""


class IssueProvider(Protocol):
    @staticmethod
    def setup():
        ...

    @staticmethod
    def begin(issue: "Issue", assign_on_begin: str, label_on_begin: str):
        ...

    @staticmethod
    def get_latest(filter_on_label: str) -> "Sequence[GithubIssue]":
        ...

    @staticmethod
    def assigned_to_me(filter_on_label: str) -> "Sequence[GithubIssue]":
        ...


def get_issue_provider(cfg: "IssueProviderConfig") -> IssueProvider:
    from lumberkid.issue_provider import github_provider

    match cfg.provider:
        case "github":
            return github_provider
