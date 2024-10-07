# Copyright Amethyst Reese
# Licensed under the MIT license

import logging
import sys
from typing import NoReturn

import click

from .core import run


@click.command()
@click.option("--debug/--quiet", default=None, help="Increase or decrease logging")
@click.option("--stress-test", "-s", is_flag=True, help="Run every test 10 times")
@click.option("--randomize", "-r", is_flag=True, help="Randomize test order")
@click.argument("module")
def main(
    debug: bool | None,
    module: str,
    randomize: bool,
    stress_test: bool,
) -> NoReturn:
    logging.basicConfig(
        level=(
            logging.DEBUG
            if debug
            else (logging.WARNING if debug is None else logging.ERROR)
        ),
        stream=sys.stderr,
    )
    result = run(module, randomize=randomize, stress_test=stress_test)
    sys.exit(0 if result.wasSuccessful() else 1)
