from typing import TYPE_CHECKING

from lumberkid.config import LumberkidConfig

if TYPE_CHECKING:
    from pathlib import Path


def test_config_retrieval(tmp_path: "Path") -> None:
    from lumberkid.config import get_config

    (tmp_path / ".lumberkid.toml").write_text(
        """
[forge]
start_as_draft = false

[issue_source]
assign_on_add = true
label_on_add = "test_label"
"""
    )
    config = get_config(tmp_path)
    assert config.forge.start_as_draft is False
    assert config.forge.assign_on_add is True
    assert config.forge.label_on_add == "test_label"
    assert config.automerge is True


def test_config_from_defaults() -> None:
    config = LumberkidConfig.from_defaults({})

    # TD: Does this fail if a key is spelt wrong in the default config?

    assert config.forge.start_as_draft is False
