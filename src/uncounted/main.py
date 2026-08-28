from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import re

CHARACTERS_PER_WORD = 6
WORDS_PER_PAGE = 250
PINFILE_NAME = "{prefix}-uncounted-pinfile.json"


@dataclasses.dataclass(frozen=True, slots=True)
class FileData:
    characters: int
    paragraphs: int
    words: int
    pages: int


@dataclasses.dataclass(frozen=True, slots=True)
class CLIFlags:
    target_path: str
    file_pattern: str
    pin: bool
    diff: bool


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


def main(cli_flags: CLIFlags) -> int:
    """The main function."""
    target_path = pathlib.Path(cli_flags.target_path)

    all_data = {}

    file: pathlib.Path

    for file in target_path.glob(cli_flags.file_pattern):
        if not file.is_file(follow_symlinks=False):
            continue

        data = parse_file_data(file)

        all_data[file.name] = data

    if cli_flags.diff:
        load_pin_file(target_path)
        print("Diff not created yet.")

    elif cli_flags.pin:
        save_pin_file(target_path, all_data)

    else:
        print_review_table(all_data)

    return 0


def parse_args(args: list[str] | None = None) -> CLIFlags:
    parser = argparse.ArgumentParser("uncounted")

    parser.add_argument("target_path", default=".")
    parser.add_argument("file_pattern", nargs="?", default="*.txt")
    parser.add_argument("--pin", action="store_true", default=False)
    parser.add_argument("--diff", action="store_true", default=False)

    parsed_args = parser.parse_args(args)

    return CLIFlags(
        target_path=parsed_args.target_path,
        file_pattern=parsed_args.file_pattern,
        pin=parsed_args.pin,
        diff=parsed_args.diff,
    )


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
