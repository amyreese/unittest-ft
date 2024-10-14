# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import logging
import sys
from typing import NoReturn

import click

from .core import DEFAULT_THREADS, run


@click.command()
@click.option("--debug", default=None, help="Enable debug logging")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Quiet output")
@click.option("--stress-test", "-s", is_flag=True, help="Run every test 10 times")
@click.option("--randomize", "-r", is_flag=True, help="Randomize test order")
@click.option(
    "--threads",
    "-j",
    type=click.IntRange(min=1),
    default=DEFAULT_THREADS,
    show_default=True,
    help="Number of threads to spawn for tests",
)
@click.argument("module")
def main(
    debug: bool,
    verbose: bool,
    quiet: bool,
    module: str,
    randomize: bool,
    stress_test: bool,
    threads: int,
) -> NoReturn:
    logging.basicConfig(
        level=(logging.DEBUG if debug else logging.WARNING),
        stream=sys.stderr,
    )
    verbosity = 2 if verbose else 0 if quiet else 1
    result = run(
        module,
        randomize=randomize,
        stress_test=stress_test,
        threads=threads,
        verbosity=verbosity,
    )
    sys.exit(0 if result.wasSuccessful() else 1)
