#!/usr/bin/env python3
"""Validate provenance/assets and, with --built, local HTML links and labels."""

import argparse

from omt.cli import run
from omt.files import REPOSITORY_ROOT
from omt.validation import check


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--built", action="store_true")
    args = parser.parse_args()
    errors = check(REPOSITORY_ROOT, built=args.built)
    if errors:
        print("\n".join(errors))
        return 1
    print("Source hashes, translation provenance, assets and requested book checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run(main))
