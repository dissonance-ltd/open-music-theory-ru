"""Shared command exit behavior; domain functions never call sys.exit()."""

import sys
from collections.abc import Callable

from lxml import etree

from .files import InputError


def run(main: Callable[[], int]) -> int:
    try:
        return main()
    except (InputError, OSError, UnicodeError, etree.LxmlError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
