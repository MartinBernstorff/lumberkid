from typing import TYPE_CHECKING, Literal, Protocol

import pydantic

if TYPE_CHECKING:
    from lumberkid.issue_provider.issues import Issue


class ForgeConfig(pydantic.BaseModel):
    provider: Literal["github"] = "github"
    start_as_draft: bool = False
    automerge: bool = True
    squash: bool = True


class Forge(Protocol):
    @staticmethod
    def setup():
        ...

    @staticmethod
    def begin(issue: "Issue", start_as_draft: bool):
        ...

    @staticmethod
    def merge(automerge: bool, squash: bool, mark_as_ready: bool):
        ...


def get_forge(cfg: "ForgeConfig") -> Forge:
    from lumberkid.forge import github_forge

    match cfg.provider:
        case "github":
            return github_forge
