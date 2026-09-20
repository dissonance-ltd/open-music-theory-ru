#!/usr/bin/env python3
"""Import configured Pressbooks pages; never overwrite Russian translations."""

import argparse
from pathlib import Path

from omt.cli import run
from omt.files import REPOSITORY_ROOT, read_json
from omt.importing import import_book
from omt.models import SourceConfig


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=REPOSITORY_ROOT / "upstream/sources.json")
    parser.add_argument("--cache", type=Path, default=REPOSITORY_ROOT / ".cache/omt")
    parser.add_argument("--output", type=Path, default=REPOSITORY_ROOT / "upstream")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument(
        "--retrieved-at", help="Actual retrieval timestamp for offline cache imports"
    )
    args = parser.parse_args()
    if args.offline and not args.retrieved_at:
        parser.error(
            "--offline requires --retrieved-at (do not relabel an old cache as freshly fetched)"
        )
    config = read_json(args.config, SourceConfig)
    manifest = import_book(
        config,
        args.cache,
        args.output,
        offline=args.offline,
        retrieved_at=args.retrieved_at,
    )
    print(
        f"Imported {len(manifest.chapters)} English snapshots. Russian chapters were not modified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run(main))
