"""Test the parsing of CLI args into a CLIArgs object."""

from __future__ import annotations

import pytest

from uncounted.main import CLIArgs
from uncounted.main import Command
from uncounted.main import parse_args


@pytest.mark.parametrize(
    "args,expected",
    (
        (
            ["stats"],
            CLIArgs(Command.STATS, ".", "*.txt"),
        ),
        (
            ["diff"],
            CLIArgs(Command.DIFF, ".", "*.txt"),
        ),
        (
            ["pin"],
            CLIArgs(Command.PIN, ".", "*.txt"),
        ),
        (
            ["stats", "--path", "/foo"],
            CLIArgs(Command.STATS, "/foo", "*.txt"),
        ),
        (
            ["stats", "--pattern", "*"],
            CLIArgs(Command.STATS, ".", "*"),
        ),
        (
            ["stats", "--path", "/foo", "--pattern", "*"],
            CLIArgs(Command.STATS, "/foo", "*"),
        ),
    ),
)
def test_command_line_argument_parsing(args: list[str], expected: CLIArgs) -> None:
    """Array of tests validating combinations of CLI options."""

    result = parse_args(args)

    assert result == expected
