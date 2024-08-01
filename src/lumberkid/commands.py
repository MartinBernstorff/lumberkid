from lumberkid.config import get_config
from lumberkid.ui import IssueSelecter


def sync() -> None:
    cfg = get_config()
    cfg.vcs.sync()


def add() -> None:
    cfg = get_config()
    source = cfg.issue_source.setup()
    selected = IssueSelecter(cfg.issue_title_parser).select_issue_dialog(
        [*source.get_latest(cfg.in_progress_label), *source.assigned_to_me(cfg.in_progress_label)]
    )
    cfg.vcs.add(selected, default_branch=cfg.default_branch, migrate_changes=cfg.migrate_changes)
    cfg.forge.setup().add(selected)


def quick_add() -> None:
    cfg = get_config()
    issue = IssueSelecter(cfg.issue_title_parser).select_issue_dialog([])
    cfg.vcs.add(issue, default_branch=cfg.default_branch, migrate_changes=cfg.migrate_changes)
    cfg.forge.setup().add(issue)


def merge() -> None:
    cfg = get_config()
    cfg.forge.setup().merge(cfg.automerge, cfg.squash)
