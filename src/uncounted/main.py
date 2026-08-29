from __future__ import annotations

import argparse
import dataclasses
import enum
import json
import pathlib
import re

CHARACTERS_PER_WORD = 6
WORDS_PER_PAGE = 250
PINFILE_NAME = "{prefix}-uncounted-pinfile.json"


class Command(enum.StrEnum):
    PIN = "pin"
    DIFF = "diff"
    STATS = "stats"


@dataclasses.dataclass(frozen=True, slots=True)
class FileData:
    characters: int
    paragraphs: int
    words: int
    pages: int


@dataclasses.dataclass(frozen=True, slots=True)
class CLIArgs:
    command: Command
    target_path: str
    file_pattern: str


def clean_whitespace(content: str) -> str:
    """Reduce all whitespace to a single instance."""
    return re.sub(r"(\s)+", r"\1", content)


def parse_file_data(file: pathlib.Path) -> FileData:
    """Read the file and return a FileData object for record."""
    contents = clean_whitespace(file.read_text())
    content_len = len(contents)

    return FileData(
        characters=content_len,
        paragraphs=contents.count("\n"),
        words=content_len // CHARACTERS_PER_WORD,
        pages=(content_len // CHARACTERS_PER_WORD) // WORDS_PER_PAGE,
    )


def print_review_table(data: dict[str, FileData]) -> None:
    """Print structured review table to stdout."""
    template = "| {file_name:<40} | {characters:>7} | {words:>7} | {paragraphs:>8} | {pages:>7} |"
    headers = {
        "file_name": "File Name",
        "characters": "Chars",
        "words": "Words",
        "paragraphs": "Breaks",
        "pages": "Pages",
    }
    header = template.replace(">", "^").format(**headers)

    print(header)
    print("-" * len(header))

    totals: dict[str, int] = {}
    for filename, filedata in data.items():
        print(template.format(file_name=filename, **dataclasses.asdict(filedata)))

        for key, value in dataclasses.asdict(filedata).items():
            totals.setdefault(key, 0)
            totals[key] += value

    print("-" * len(header))

    print(template.format(file_name="Total", **totals))


def save_pin_file(target_path: pathlib.Path, filedata: dict[str, FileData]) -> None:
    """Save a pin file if it does not already exist."""
    file_name = PINFILE_NAME.format(prefix=target_path.name)
    target_file = target_path / file_name

    if target_file.exists():
        print("Cannot pin. Pin file already exists.")

    else:

        with open(target_file, "w", encoding="utf-8") as outfile:
            json.dump(filedata, outfile, indent=4, default=dataclasses.asdict)

        print(f"Saved pin file: {target_file}")


def load_pin_file(target_path: pathlib.Path) -> dict[str, FileData]:
    """Load a pin file if it exists."""
    file_name = PINFILE_NAME.format(prefix=target_path.name)
    target_file = target_path / file_name

    if not target_file.exists():
        print(f"Cannot load pin file. {target_file} does not exist.")

    return {}


def main(cli_args: CLIArgs) -> int:
    """The main function."""
    target_path = pathlib.Path(cli_args.target_path)

    all_data = {}

    file: pathlib.Path

    files = list(target_path.glob(cli_args.file_pattern))

    if not len(files):
        print(f"No files discovered. '{cli_args.target_path}' - '{cli_args.file_pattern}'")
        return 0

    for file in files:
        if not file.is_file(follow_symlinks=False):
            continue

        data = parse_file_data(file)

        all_data[file.name] = data

    if cli_args.command is Command.DIFF:
        load_pin_file(target_path)
        print("Diff not created yet.")

    elif cli_args.command is Command.PIN:
        save_pin_file(target_path, all_data)

    else:
        print_review_table(all_data)

    return 0


def parse_args(args: list[str] | None = None) -> CLIArgs:
    parser = argparse.ArgumentParser("uncounted")

    parser.add_argument(
        "command",
        default="stats",
        nargs="?",
        choices=("pin", "diff", "stats"),
        help="Command to run. Default is 'stats'",
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Define the working path. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--pattern",
        default="*.txt",
        help="Glob pattern of files to process. Not recursive.",
    )

    parsed_args = parser.parse_args(args)

    return CLIArgs(
        command=Command(parsed_args.command),
        target_path=parsed_args.path,
        file_pattern=parsed_args.pattern,
    )


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
