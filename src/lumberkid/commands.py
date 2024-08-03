from lumberkid.config import LumberkidApp, get_config
from lumberkid.forge.forge import get_forge
from lumberkid.forge.github_forge import parse_issue_title
from lumberkid.issue_provider.issue_provider import get_issue_provider
from lumberkid.ui import IssueSelecter
from lumberkid.vcs.vcs import get_vcs


def get_app() -> LumberkidApp:
    cfg = get_config()
    return LumberkidApp(
        forge=get_forge(cfg.forge), issues=get_issue_provider(cfg.issues), vcs=get_vcs(cfg.vcs)
    )


def sync() -> None:
    cfg = get_config()
    get_vcs(cfg.vcs).sync()


def begin() -> None:
    cfg = get_config()
    app = get_app()
    source = app.issues
    selected = IssueSelecter(parse_issue_title).select_issue_dialog(
        [
            *source.get_latest(cfg.issues.label_on_begin),
            *source.assigned_to_me(cfg.issues.label_on_begin),
        ]
    )
    app.vcs.begin(
        selected, default_branch=cfg.vcs.default_branch, migrate_changes=cfg.vcs.migrate_changes
    )
    source.begin(selected, cfg.issues.assign_on_begin, cfg.issues.label_on_begin)

    app.forge.setup()
    app.forge.begin(selected, cfg.forge.start_as_draft)


def quick_add() -> None:
    cfg = get_config()
    app = get_app()
    issue = IssueSelecter(parse_issue_title).select_issue_dialog([])
    app.vcs.begin(
        issue, default_branch=cfg.vcs.default_branch, migrate_changes=cfg.vcs.migrate_changes
    )
    app.forge.setup()
    app.forge.begin(issue, cfg.forge.start_as_draft)


def merge() -> None:
    cfg = get_config()
    forge = get_forge(cfg.forge)
    forge.setup()
    forge.merge(cfg.forge.automerge, cfg.forge.squash, mark_as_ready=cfg.forge.start_as_draft)
