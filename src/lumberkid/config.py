from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Mapping, Type

import tomllib

from lumberkid.git import GitVCS
from lumberkid.github import GithubForge, GithubIssueProvider, parse_issue_title

if TYPE_CHECKING:
    from lumberkid.issues import IssueTitle


def deep_merge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    result = dict1.copy()
    for key, value in dict2.items():
        # Combine dicts
        original_contains_dict = (
            isinstance(value, dict) and key in result and isinstance(result[key], dict)
        )
        if original_contains_dict:
            result[key] = deep_merge(result[key], value)  # type: ignore
        # Combined lists
        elif isinstance(value, list) and key in result and isinstance(result[key], list):
            result[key] = result[key] + value
        else:
            result[key] = value
    return result


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
    def from_defaults(
        cls: Type["LumberkidConfig"], overrides: dict[str, Any] | None = None
    ) -> "LumberkidConfig":
        if overrides is None:
            overrides = {}
        default_config: dict[str, Any] = load_toml(Path(__file__).parent / "default_config.toml")  # type: ignore
        merged: Mapping[str, Any] = deep_merge(default_config, overrides)

        return cls(
            forge=GithubForge.from_toml(merged),  # type: ignore
            issue_source=GithubIssueProvider.from_toml(merged["issue_source"]),  # type: ignore
            issue_title_parser=parse_issue_title,
            in_progress_label=merged["issue_source"]["in_progress_label"],  # type: ignore
            default_branch=merged["vcs"]["default_branch"],  # type: ignore
            migrate_changes=merged["lumberkid"]["migrate_changes"],  # type: ignore
            automerge=merged["forge"]["automerge"],  # type: ignore
            squash=merged["forge"]["squash"],  # type: ignore
            vcs=GitVCS.from_toml(merged["vcs"]),  # type: ignore
        )

    @classmethod
    def from_toml(cls: Type["LumberkidConfig"], path: "Path") -> "LumberkidConfig":
        toml = load_toml(path)

        return cls.from_defaults(toml if toml is not None else {})


def load_toml(path: "Path") -> dict[str, Any] | None:
    try:
        with open(path, "rb") as f:  # noqa: PTH123
            return tomllib.load(f)
    except FileNotFoundError:
        return None


def get_closest_config(starting_path: "Path") -> LumberkidConfig | None:
    """Get the config from the closest parent directory. If no config is found in cwd, move up a dir, and try again. If no config is found, return None."""
    cwd = starting_path
    while cwd.exists():
        config_path = cwd / ".lumberkid.toml"
        if config_path.exists():
            return LumberkidConfig.from_toml(config_path)

        has_parent = cwd.parent != cwd
        if not has_parent:
            break
        cwd = cwd.parent
    return None


def get_config(starting_path: Path | None = None) -> LumberkidConfig:
    """Get the config. In the future, will look for an XDG-compatible .toml"""
    if starting_path is None:
        starting_path = Path.cwd()

    closest_config = get_closest_config(starting_path)

    return closest_config or LumberkidConfig.from_defaults({})


if __name__ == "__main__":
    config = get_config()
