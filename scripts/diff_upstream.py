#!/usr/bin/env python3
"""Compare source manifests: exit 0 if unchanged, 1 if changed, 2 on input errors."""

import argparse
from pathlib import Path

from omt.cli import run
from omt.comparison import compare
from omt.files import encode_json, read_json
from omt.models import SourceManifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    args = parser.parse_args()
    previous = read_json(args.old, SourceManifest)
    current = read_json(args.new, SourceManifest)
    changes = compare(previous, current)
    print(encode_json(changes).decode("utf-8"), end="")
    return int(changes.has_changes)


if __name__ == "__main__":
    raise SystemExit(run(main))
