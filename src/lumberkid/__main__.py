import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

import typer

from . import commands as cmd

if TYPE_CHECKING:
    from collections.abc import Sequence

app = typer.Typer(
    name="[l]umber[m]an",
    no_args_is_help=True,
    add_help_option=True,
    add_completion=False,
    help="All commands are registered as [sh]orthand. You can call the command as 'lk sh' or 'lumberkid shorthand'.",
)


@dataclass(frozen=True)
class Command:
    name: str
    fn: Callable[[], None]


@dataclass(frozen=True)
class CommandSection:
    name: str
    commands: "Sequence[Command]"


commands = [
    CommandSection(
        name="Change Manager",
        commands=[
            Command(name="[a]dd", fn=cmd.add),
            Command(name="[q]uick-add", fn=cmd.quick_add),
            Command(name="[s]ync", fn=cmd.sync),
            Command(name="[m]erge", fn=cmd.merge),
        ],
    )
]

shorthands: set[str] = set()
for section in commands:
    for command in section.commands:
        # Add the combined command, e.g. [i]nsert
        app.command(name=command.name, rich_help_panel=section.name)(command.fn)

        # Handle shorthand, e.g. i
        command_shorthand = re.findall(r"\[(.*?)\]", command.name)[0]
        if command_shorthand in shorthands:
            raise ValueError(f"Duplicate shorthand '{command_shorthand}'")

        shorthands.add(command_shorthand)
        app.command(name=command_shorthand, hidden=True)(command.fn)

        # Add the full command, e.g. insert
        command_full = command.name.replace("[", "").replace("]", "")
        app.command(name=command_full, hidden=True)(command.fn)

if __name__ == "__main__":
    app()
