from dataclasses import dataclass, field
from os import close
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Mapping, Type, TypeVar, override

import platformdirs
import tomllib

from lumberkid.git import GitVCS
from lumberkid.github import GithubForge, GithubIssueProvider, parse_issue_title

if TYPE_CHECKING:
    from lumberkid.issues import IssueTitle

S = TypeVar("S")


@dataclass(frozen=True)
class LumberkidConfig:
    forge: GithubForge

    issue_source: GithubIssueProvider
    issue_title_parser: Callable[[str], "IssueTitle"]
    in_progress_label: str

    default_branch: str
    migrate_changes: bool

    automerge: bool
    squash: bool

    vcs: GitVCS

    @classmethod
    def _get_forge(cls: Type["LumberkidConfig"], toml: Mapping[str, Any] | None) -> GithubForge:
        try:
            return GithubForge.from_toml(toml["forge"])  # type: ignore
        except KeyError:
            return GithubForge(start_as_draft=False, assign_on_add=False, label_on_add=None)

    @classmethod
    def _get_issue_source(
        cls: Type["LumberkidConfig"], toml: Mapping[str, Any] | None
    ) -> GithubIssueProvider:
        try:
            return GithubIssueProvider.from_toml(toml["issue_source"])  # type: ignore
        except KeyError:
            return GithubIssueProvider()

    @classmethod
    def _get_vcs(cls: Type["LumberkidConfig"], toml: Mapping[str, Any] | None) -> GitVCS:
        try:
            return GitVCS.from_toml(toml["vcs"])  # type: ignore
        except KeyError:
            return GitVCS()

    @classmethod
    def from_defaults(
        cls: Type["LumberkidConfig"], overrides: Mapping[str, Any] = {}
    ) -> "LumberkidConfig":
        default_config = load_toml(Path(__file__).parent / "default_config.toml")
        merged: Mapping[str, Any] = {**default_config, **overrides}  # type: ignore

        return cls(
            forge=cls._get_forge(merged),
            issue_source=cls._get_issue_source(merged),
            issue_title_parser=parse_issue_title,
            in_progress_label=merged["issue_source"]["in_progress_label"],  # type: ignore
            default_branch=merged["vcs"]["default_branch"],  # type: ignore
            migrate_changes=merged["lumberkid"]["migrate_changes"],  # type: ignore
            automerge=merged["forge"]["automerge"],  # type: ignore
            squash=merged["forge"]["squash"],  # type: ignore
            vcs=cls._get_vcs(merged),
        )

    @classmethod
    def from_toml(cls: Type["LumberkidConfig"], path: "Path") -> "LumberkidConfig":
        toml = load_toml(path)

        return cls.from_defaults(toml if toml is not None else {})


def load_toml(path: "Path") -> Mapping[str, Any] | None:
    try:
        with open(path, "rb") as f:  # noqa: PTH123
            return tomllib.load(f)
    except FileNotFoundError:
        return None


def _get_closest_config(starting_path: "Path") -> LumberkidConfig | None:
    """Get the config from the closest parent directory. If no config is found in cwd, move up a dir, and try again. If no config is found, return None."""
    cwd = starting_path
    while cwd.exists():
        config_path = cwd / ".lumberkid.toml"
        if config_path.exists():
            return LumberkidConfig.from_toml(config_path)
        cwd = cwd.parent
    return None


def get_config(starting_path: Path | None = None) -> LumberkidConfig:
    """Get the config. In the future, will look for an XDG-compatible .toml"""
    if starting_path is None:
        starting_path = Path.cwd()

    closest_config = _get_closest_config(starting_path)

    return closest_config or LumberkidConfig.from_defaults({})


if __name__ == "__main__":
    config = get_config()
