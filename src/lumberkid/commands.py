from lumberkid.config import get_config
from lumberkid.ui import IssueSelecter


def sync() -> None:
    cfg = get_config()
    cfg.vcs.sync()


def begin() -> None:
    cfg = get_config()
    source = cfg.issue_source.setup()
    selected = IssueSelecter(cfg.issue_title_parser).select_issue_dialog(
        [
            *source.get_latest(cfg.issue_source.label_on_begin),
            *source.assigned_to_me(cfg.issue_source.label_on_begin),
        ]
    )
    cfg.vcs.begin(selected, default_branch=cfg.default_branch, migrate_changes=cfg.migrate_changes)
    cfg.issue_source.begin(selected)
    cfg.forge.setup().begin(selected)


def quick_add() -> None:
    cfg = get_config()
    issue = IssueSelecter(cfg.issue_title_parser).select_issue_dialog([])
    cfg.vcs.begin(issue, default_branch=cfg.default_branch, migrate_changes=cfg.migrate_changes)
    cfg.forge.setup().begin(issue)


def merge() -> None:
    cfg = get_config()
    cfg.forge.setup().merge(cfg.automerge, cfg.squash)
