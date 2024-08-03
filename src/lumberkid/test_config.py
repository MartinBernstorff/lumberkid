from pathlib import Path

import tomli_w

from lumberkid.config import LumberkidConfig, get_closest_config, get_config


def test_config_upwards_traversal(tmp_path: "Path") -> None:
    (tmp_path / ".lumberkid.toml").write_text(
        """
[forge]
start_as_draft = false

[issues]
assign_on_begin = "@me"
label_on_begin = "test_label"
"""
    )

    # To check upwards traversal, we need to create a child directory
    child_dir = tmp_path / "a" / "b"
    child_dir.mkdir(parents=True)
    config = get_config(child_dir)

    assert config.forge.start_as_draft is False
    assert config.issues.assign_on_begin == "@me"
    assert config.issues.label_on_begin == "test_label"
    assert config.forge.automerge is True


def test_no_parent_config_found() -> None:
    config = get_closest_config(Path())
    assert config is None


def test_config_from_defaults() -> None:
    config = LumberkidConfig()

    assert config.forge.start_as_draft is False


def test_write_default_config() -> None:
    project_dir = Path(__file__).parent.parent.parent
    toml = tomli_w.dumps(LumberkidConfig().model_dump())
    (project_dir / ".default_config.toml").write_text(toml)
