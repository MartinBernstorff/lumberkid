from lumberkid.issue_provider.issues import Issue, RemoteIssue
from lumberkid.subprocess_utils import interactive_cmd, shell_output


def _branch_title(issue: "Issue") -> str:
    match issue:
        case RemoteIssue():
            base_name = f"{issue.title.content}/{issue.entity_id}"
        case Issue():
            base_name = f"{issue.title.content}"

    return base_name.replace(" ", "_")


def _git_clean() -> bool:
    git_status = shell_output("git status --porcelain")
    return git_status is None or git_status.strip() != ""


def begin(issue: "Issue", default_branch: str, migrate_changes: bool):
    needs_migration = migrate_changes and not _git_clean()

    if needs_migration:
        interactive_cmd("git stash")
    interactive_cmd(
        [
            "git fetch origin",
            f"git checkout -b {_branch_title(issue)} --no-track origin/{default_branch}",
        ]
    )
    if needs_migration:
        interactive_cmd("git stash pop")
    interactive_cmd([f"git commit --allow-empty -m '{_branch_title(issue)}'", "git push"])


def sync():
    interactive_cmd(["git pull origin main", "git push"])
