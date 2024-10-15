# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import importlib
import logging
import os
import random
import sys
import time
from collections import defaultdict
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from typing import Any, Generator, TextIO
from unittest import TestCase, TestLoader, TestResult, TestSuite

from typing_extensions import Self

LOG = logging.getLogger(__name__)

DEFAULT_THREADS = (os.cpu_count() or 4) + 2


class FTTestResult(TestResult):
    def __init__(
        self,
        stream: TextIO | None = None,
        descriptions: bool | None = None,
        verbosity: int | None = None,
        *,
        stress_test: bool = False,
    ) -> None:
        super().__init__(stream=stream, descriptions=descriptions, verbosity=verbosity)
        self.verbosity = verbosity or 1
        self.before = time.monotonic_ns()
        self.duration = 0
        self.collected_duration = 0
        self.stress_test = stress_test

    def stopTest(self, test: Any) -> None:
        super().stopTest(test)
        self.duration = time.monotonic_ns() - self.before

    def stopTestRun(self) -> None:
        super().stopTestRun()
        self.duration = time.monotonic_ns() - self.before

    def __str__(self) -> str:
        items: dict[tuple[str, str], int] = defaultdict(int)
        for test_case, trace in self.errors:
            items[f"ERROR: {test_case}", trace] += 1
        for test_case, trace in self.failures:
            items[f"FAIL: {test_case}", trace] += 1

        if self.stress_test:
            results = {
                f"{label} (x{count})": trace for (label, trace), count in items.items()
            }
        else:
            results = {f"{label}": trace for (label, trace), count in items.items()}
        longest = max(len(label) for label in results) if results else 70

        msg = "\n"
        msg += "\n".join(
            f"{'=' * longest}\n{label}\n{'-' * longest}\n{trace}"
            for label, trace in results.items()
        )
        msg += "-" * longest
        msg += f"\nRan {self.testsRun} tests in {format_ns(self.duration)}"

        saved = self.collected_duration - self.duration
        if saved > 0 and (saved / self.duration) > 0.10:
            msg += f" (saved {format_ns(self.collected_duration - self.duration)})"
        msg += "\n\n"

        msg += "OK" if self.wasSuccessful() else "FAILED"

        parts = []
        if self.errors:
            parts += [f"errors={len(self.errors)}"]
        if self.failures:
            parts += [f"failures={len(self.failures)}"]
        if self.skipped:
            parts += [f"skipped={len(self.skipped)}"]
        if self.expectedFailures:
            parts += [f"expected failures={len(self.expectedFailures)}"]

        if parts:
            msg += f" ({', '.join(parts)})"

        return msg

    def __add__(self, other: object) -> FTTestResult:
        if not isinstance(other, TestResult):
            return NotImplemented
        result = FTTestResult()
        # result.collectedDurations = self.collectedDurations + other.collectedDurations
        result.errors = self.errors + other.errors
        result.expectedFailures = self.expectedFailures + other.expectedFailures
        result.failures = self.failures + other.failures
        result.skipped = self.skipped + other.skipped
        result.testsRun = self.testsRun + other.testsRun
        result.unexpectedSuccesses = (
            self.unexpectedSuccesses + other.unexpectedSuccesses
        )
        if isinstance(other, FTTestResult):
            result.collected_duration = self.duration + other.duration
        return result

    def __iadd__(self, other: object) -> Self:
        if not isinstance(other, TestResult):
            return NotImplemented
        # self.collectedDurations += other.collectedDurations
        self.errors += other.errors
        self.expectedFailures += other.expectedFailures
        self.failures += other.failures
        self.skipped += other.skipped
        self.testsRun += other.testsRun
        self.unexpectedSuccesses += other.unexpectedSuccesses
        if isinstance(other, FTTestResult):
            self.collected_duration += other.duration
        return self


def get_individual_tests(suite: TestSuite) -> Generator[TestCase, None, None]:
    for test in suite:
        if isinstance(test, TestSuite):
            yield from get_individual_tests(test)
        else:
            yield test


def run_single_test(test_id: str) -> tuple[str, FTTestResult]:
    LOG.debug("Loading test %s", test_id)
    loader = TestLoader()
    suite = loader.loadTestsFromName(test_id)
    LOG.debug("Running test %s", test_id)
    result = FTTestResult(descriptions=True, verbosity=2)
    suite.run(result)
    LOG.debug("Finished test %s", test_id)
    return (test_id, result)


def format_ns(duration: int) -> str:
    if duration < 1_000_000_000:
        return f"{duration / 1_000_000:.2f}ms"
    else:
        return f"{duration / 1_000_000_000:.3f}s"


@dataclass
class Output:
    futures: dict[Future[tuple[str, FTTestResult]], str]
    stream: TextIO = sys.stdout
    verbosity: int = 1

    def __post_init__(self) -> None:
        self.count = 0
        self.total = len(self.futures)

    def render(
        self, future: Future[tuple[str, FTTestResult]], test_result: FTTestResult
    ) -> None:
        test_id = self.futures[future]
        stream = self.stream
        verbosity = self.verbosity

        self.count += 1
        if verbosity == 2:
            stream.write(
                f"[{self.count}/{self.total}] {test_id}"
                f" ... {'OK' if test_result.wasSuccessful() else 'FAIL'} "
                f" {format_ns(test_result.duration)}\n"
            )
        elif verbosity == 1:
            if test_result.errors:
                stream.write("E")
            elif test_result.failures:
                stream.write("F")
            elif test_result.expectedFailures:
                stream.write("x")
            elif test_result.skipped:
                stream.write("s")
            else:
                stream.write(".")
        stream.flush()


def run(
    module: str = "",
    *,
    randomize: bool = False,
    stress_test: bool = False,
    threads: int = DEFAULT_THREADS,
    verbosity: int = 1,
) -> TestResult:
    loader = TestLoader()
    if module:
        try:
            loaded_module = importlib.import_module(module)
            suite = loader.loadTestsFromModule(loaded_module)
        except ImportError:
            suite = loader.discover(module)
    else:
        suite = loader.discover(".")
    LOG.debug("loaded %d test cases from %s", suite.countTestCases(), module or ".")

    test_ids = [test.id() for test in get_individual_tests(suite)]
    if stress_test:
        test_ids = test_ids * 10
    if randomize:
        random.shuffle(test_ids)
    else:
        test_ids.sort()

    LOG.debug("ready to run %d tests:\n  %s", len(test_ids), "\n  ".join(test_ids))
    pool = ThreadPoolExecutor(max_workers=threads)
    futures = {pool.submit(run_single_test, test_id): test_id for test_id in test_ids}
    pending = set(futures)

    output = Output(futures, verbosity=verbosity)
    result = FTTestResult(stress_test=stress_test)
    while pending:
        done, pending = wait(pending, timeout=0.1, return_when=FIRST_COMPLETED)
        for fut in done:
            _, test_result = fut.result()
            result += test_result
            output.render(fut, test_result)
    result.stopTestRun()

    print(result)

    return result
