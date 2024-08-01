from pathlib import Path

from lumberkid.config import LumberkidConfig, get_closest_config, get_config


def test_config_upwards_traversal(tmp_path: "Path") -> None:
    (tmp_path / ".lumberkid.toml").write_text(
        """
[forge]
start_as_draft = false

[issue_source]
assign_on_add = true
label_on_add = "test_label"
"""
    )

    # To check upwards traversal, we need to create a child directory
    child_dir = tmp_path / "a" / "b"
    child_dir.mkdir(parents=True)
    config = get_config(child_dir)

    assert config.forge.start_as_draft is False
    assert config.forge.assign_on_add is True
    assert config.forge.label_on_add == "test_label"
    assert config.automerge is True


def test_no_parent_config_found() -> None:
    config = get_closest_config(Path())
    assert config is None


def test_config_from_defaults() -> None:
    config = LumberkidConfig.from_defaults({})

    # TD: Does this fail if a key is spelt wrong in the default config?

    assert config.forge.start_as_draft is False
