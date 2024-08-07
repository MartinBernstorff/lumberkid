from dataclasses import dataclass
from pathlib import Path

import pydantic
import toml
from pydantic import ConfigDict

from lumberkid.forge.forge import Forge, ForgeConfig
from lumberkid.issue_provider.issue_provider import IssueProvider, IssueProviderConfig
from lumberkid.vcs.vcs import VCS, VCSConfig


class LumberkidBaseConfig(pydantic.BaseModel):
    model_config = ConfigDict(extra="forbid")


class LumberkidConfig(LumberkidBaseConfig):
    forge: "ForgeConfig" = ForgeConfig()
    issues: "IssueProviderConfig" = IssueProviderConfig()
    vcs: "VCSConfig" = VCSConfig()


@dataclass(frozen=True)
class LumberkidApp:
    forge: Forge
    issues: IssueProvider
    vcs: VCS


def get_closest_config(starting_path: "Path") -> LumberkidConfig | None:
    """Get the config from the closest parent directory. If no config is found in cwd, move up a dir, and try again. If no config is found, return None."""
    cwd = starting_path
    while cwd.exists():
        config_path = cwd / ".lumberkid.toml"
        if config_path.exists():
            return LumberkidConfig(**toml.load(config_path))

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

    return closest_config or LumberkidConfig()
