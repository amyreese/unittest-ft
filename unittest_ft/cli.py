# Copyright Amethyst Reese
# Licensed under the MIT license

import sys
from typing import NoReturn

from .core import run


def main() -> NoReturn:
    module = sys.argv[1]
    result = run(module)
    sys.exit(0 if result.wasSuccessful() else 1)
