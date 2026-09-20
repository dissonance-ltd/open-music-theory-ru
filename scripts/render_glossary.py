#!/usr/bin/env python3
"""Render the YAML glossary, or verify its committed Markdown with --check."""

import argparse

from omt.cli import run
from omt.files import REPOSITORY_ROOT, read_yaml, write_bytes
from omt.glossary import render
from omt.models import Glossary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    glossary = read_yaml(REPOSITORY_ROOT / "glossary/terminology.yml", Glossary)
    expected = render(glossary)
    path = REPOSITORY_ROOT / "src/glossary.md"
    if args.check:
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            print("Regenerate glossary: python scripts/render_glossary.py")
            return 1
    else:
        write_bytes(path, expected.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(run(main))
