# Copyright Amethyst Reese
# Licensed under the MIT license

import logging
import sys
import time
from unittest import expectedFailure, skip, TestCase


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.ERROR)


class SmokeTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        LOG.warning("setUpClass")

    def setUp(self) -> None:
        LOG.info("setUp")
        time.sleep(0.02)

    def tearDown(self) -> None:
        time.sleep(0.05)

    def test_python_version(self) -> None:
        self.assertGreaterEqual(sys.version_info, (3, 10))

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

    def test_sleep_1(self) -> None:
        time.sleep(1)

    def test_sleep_2(self) -> None:
        time.sleep(2)
