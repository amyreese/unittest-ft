# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import importlib
import logging
import os
import random
import time
from concurrent.futures import as_completed, ThreadPoolExecutor
from typing import Generator
from unittest import TestCase, TestLoader, TestResult, TestSuite

from rich import print
from typing_extensions import Self

LOG = logging.getLogger(__name__)

DEFAULT_THREADS = (os.cpu_count() or 4) + 2


class FTTestResult(TestResult):
    def __str__(self) -> str:
        items = [(f"ERROR: {test_case}", trace) for test_case, trace in self.errors]
        items += [(f"FAIL: {test_case}", trace) for test_case, trace in self.failures]

        longest = max(len(label) for label, _ in items) if items else 70

        msg = "\n".join(
            f"{'=' * longest}\n{label}\n{'-' * longest}\n{trace}"
            for label, trace in items
        )
        msg += "-" * longest

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
        return self


def get_individual_tests(suite: TestSuite) -> Generator[TestCase, None, None]:
    for test in suite:
        if isinstance(test, TestSuite):
            yield from get_individual_tests(test)
        else:
            yield test


def run_single_test(test_id: str) -> tuple[str, TestResult, int]:
    LOG.debug("Loading test %s", test_id)
    loader = TestLoader()
    result = FTTestResult(descriptions=True, verbosity=2)
    suite = loader.loadTestsFromName(test_id)
    LOG.debug("Running test %s", test_id)
    before = time.monotonic_ns()
    suite.run(result)
    duration = time.monotonic_ns() - before
    LOG.debug("Finished test %s", test_id)
    return (test_id, result, duration)


def format_ns(duration: int) -> str:
    if duration < 1_000_000_000:
        return f"{duration / 1_000_000:.2f}ms"
    else:
        return f"{duration / 1_000_000_000:.3f}s"


def run(
    module: str,
    *,
    randomize: bool = False,
    stress_test: bool = False,
    threads: int = DEFAULT_THREADS,
) -> TestResult:
    loaded_module = importlib.import_module(module)
    loader = TestLoader()
    suite = loader.loadTestsFromModule(loaded_module)
    LOG.debug("loaded %d test cases from %s", suite.countTestCases(), module)

    before = time.monotonic_ns()
    test_ids = [test.id() for test in get_individual_tests(suite)]
    if stress_test:
        test_ids = test_ids * 10
    if randomize:
        random.shuffle(test_ids)
    else:
        test_ids.sort()

    LOG.debug("ready to run %d tests:\n  %s", len(test_ids), "\n  ".join(test_ids))
    pool = ThreadPoolExecutor(max_workers=threads)
    futs = [pool.submit(run_single_test, test_id) for test_id in test_ids]

    test_duration = 0
    result = FTTestResult()

    for fut in as_completed(futs):
        test_id, test_result, duration = fut.result()
        print(
            f"{test_id} ... {'OK' if test_result.wasSuccessful() else 'FAIL'} "
            f" {format_ns(duration)}"
        )

        test_duration += duration
        result += test_result

    runner_duration = time.monotonic_ns() - before

    print()
    print(result)
    print(
        f"Ran {len(test_ids)} tests in {format_ns(runner_duration)} "
        f"(saved {format_ns(test_duration - runner_duration)})\n"
    )

    if result.wasSuccessful():
        print("OK")
    else:
        print("FAILED")

    return result
