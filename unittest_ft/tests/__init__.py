# Copyright Amethyst Reese
# Licensed under the MIT license

import sys
from unittest import TestCase


class SmokeTest(TestCase):
    def test_python_version(self) -> None:
        self.assertGreaterEqual(sys.version_info, (3, 10))
