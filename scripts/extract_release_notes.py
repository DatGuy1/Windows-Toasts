"""
Prints the CHANGELOG.rst section for a release tag, as reStructuredText. The deploy workflow converts it to Markdown
with pandoc and uses it as the GitHub release notes.

Usage: python scripts/extract_release_notes.py v1.4.0
"""

import re
import sys
from pathlib import Path

CHANGELOG_PATH = Path(__file__).parent.parent / "CHANGELOG.rst"


def parse_sections(changelog: str) -> dict[str, str]:
    """Maps each section title (a line underlined with =) to its body"""
    lines = changelog.splitlines()
    starts = [i for i in range(len(lines) - 1) if lines[i] and re.fullmatch(r"=+", lines[i + 1])]
    return {
        lines[start]: "\n".join(lines[start + 2 : end]).strip()
        for start, end in zip(starts, [*starts[1:], len(lines)], strict=True)
    }


def find_notes(sections: dict[str, str], tag: str) -> str | None:
    version = tag.removeprefix("v")
    titleRegex = re.compile(rf"{re.escape(version)} \(\d{{4}}-\d{{2}}-\d{{2}}\)")
    notes = next((body for title, body in sections.items() if titleRegex.fullmatch(title)), None)
    return notes or None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    tag = argv[1]
    notes = find_notes(parse_sections(CHANGELOG_PATH.read_text(encoding="utf-8")), tag)
    if notes is None:
        print(f"CHANGELOG.rst has no dated, non-empty section for {tag}", file=sys.stderr)
        return 1

    print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
