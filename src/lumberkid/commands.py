from lumberkid.config import SyncOn, get_config
from lumberkid.ui import IssueSelecter

cfg = get_config()


def sync() -> None:
    cfg.vcs.sync()


def add() -> None:
    source = cfg.issue_source.setup()
    selected = IssueSelecter(cfg.issue_title_parser).select_issue_dialog(
        [*source.get_latest(cfg.in_progress_label), *source.assigned_to_me(cfg.in_progress_label)]
    )

    cfg.vcs.add(selected)
    cfg.forge.add(selected)

    if cfg.sync_on == SyncOn.ALL:
        sync()


def quick_add() -> None:
    issue = IssueSelecter(cfg.issue_title_parser).select_issue_dialog([])

    if cfg.sync_on == SyncOn.ALL:
        sync()

    cfg.vcs.add(issue)
    cfg.forge.add(issue)


def merge() -> None:
    cfg.vcs.sync()
    cfg.forge.merge(cfg.automerge, cfg.squash)
