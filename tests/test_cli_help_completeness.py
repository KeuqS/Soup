"""Keep visible CLI commands and parameters discoverable in ``--help``."""

from collections.abc import Iterator

import click
import typer

from soup_cli.cli import app


def _visible_commands(
    command: click.Command, path: tuple[str, ...] = ()
) -> Iterator[tuple[tuple[str, ...], click.Command]]:
    """Yield visible commands in the complete Typer command tree."""
    if getattr(command, "hidden", False):
        return
    yield path, command
    if isinstance(command, click.Group):
        for name, child in command.commands.items():
            yield from _visible_commands(child, path + (name,))


def test_visible_commands_and_parameters_have_help() -> None:
    """Every visible CLI entry should explain itself in generated help."""
    root = typer.main.get_command(app)
    missing: list[str] = []

    for path, command in _visible_commands(root):
        label = " ".join(path) or "soup"
        if path and not command.help:
            missing.append(f"command {label!r}")
        for parameter in command.params:
            if getattr(parameter, "hidden", False):
                continue
            if not parameter.help:
                missing.append(f"parameter {label!r}: {parameter.name!r}")

    assert not missing, "Missing CLI help:\n" + "\n".join(missing)
