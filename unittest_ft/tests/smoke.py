# Copyright Amethyst Reese
# Licensed under the MIT license

import sys
from unittest import expectedFailure, skip, TestCase


class SmokeTest(TestCase):
    def test_python_version(self) -> None:
        self.assertGreaterEqual(sys.version_info, (3, 8))

    def test_nothing(self) -> None:
        pass

    @skip("because")
    def test_skipping(self) -> None:
        pass

    @expectedFailure
    def test_expected_failure(self) -> None:
        self.fail("🍉")

    @expectedFailure
    def test_subtests(self) -> None:
        with self.subTest("success"):
            pass

        with self.subTest("failure"):
            self.fail("🐈")

    def test_spin_ten_thousand(self) -> None:
        total = 0
        for k in range(10_000):
            value = k // 37
            total += value
        self.assertEqual(total, 1346355)

    def test_spin_ten_million(self) -> None:
        total = 0
        for k in range(10_000_000):
            value = k // 37
            total += value
        self.assertEqual(total, 1351346351355)
