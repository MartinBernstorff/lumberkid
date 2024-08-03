from typing import TYPE_CHECKING, Literal, Protocol

import pydantic

if TYPE_CHECKING:
    from lumberkid.issue_provider.issues import Issue


class VCSConfig(pydantic.BaseModel):
    provider: Literal["git"] = "git"
    default_branch: str = "main"
    migrate_changes: bool = True


class VCS(Protocol):
    @staticmethod
    def begin(issue: "Issue", default_branch: str, migrate_changes: bool):
        ...

    @staticmethod
    def sync():
        ...


def get_vcs(cfg: "VCSConfig") -> VCS:
    from lumberkid.vcs import git_vcs

    match cfg.provider:
        case "git":
            return git_vcs
