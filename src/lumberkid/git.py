from typing import TYPE_CHECKING

from lumberkid.issues import Issue, RemoteIssue
from lumberkid.subprocess_utils import interactive_cmd


def _branch_title(issue: "Issue") -> str:
    match issue:
        case RemoteIssue():
            base_name = f"{issue.title.content}/{issue.entity_id}"
        case Issue():
            base_name = f"{issue.title.content}"

    return base_name.replace(" ", "_")


class GitVCS:
    def add(self, issue: "Issue"):
        interactive_cmd([f"git checkout -b {_branch_title(issue)}"])

    def sync(self):
        interactive_cmd(["git pull origin main", "git push"])
