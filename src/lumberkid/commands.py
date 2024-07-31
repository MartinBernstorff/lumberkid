
from lumberkid.config import get_config
from lumberkid.ui import IssueSelecter

cfg = get_config()


def sync() -> None:
    cfg.vcs.sync()


def add() -> None:
    source = cfg.issue_source.setup()
    selected = IssueSelecter(cfg.issue_title_parser).select_issue_dialog(
        [*source.get_latest(cfg.in_progress_label), *source.assigned_to_me(cfg.in_progress_label)]
    )
    cfg.vcs.add(selected, default_branch=cfg.default_branch, migrate_changes=cfg.migrate_changes)
    cfg.forge.add(selected)


def quick_add() -> None:
    issue = IssueSelecter(cfg.issue_title_parser).select_issue_dialog([])
    cfg.vcs.add(issue, default_branch=cfg.default_branch, migrate_changes=cfg.migrate_changes)
    cfg.forge.add(issue)


def merge() -> None:
    cfg.forge.merge(cfg.automerge, cfg.squash)
