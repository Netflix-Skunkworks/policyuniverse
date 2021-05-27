#     Copyright 2014 Netflix, Inc.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
"""
.. module: policyuniverse.tests.test_common
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  George Psarakis <giwrgos.psarakis@gmail.com>

"""
import unittest
from collections.abc import Sequence

from policyuniverse.common import ensure_array, is_array


class CustomSequence(Sequence):
    def __init__(self, *elements):
        self._elements = elements

    def __getitem__(self, item):
        return self._elements[item]

    def __len__(self):
        return self._elements.__len__()

    def __iter__(self):
        return iter(self._elements)


class CommonTestCase(unittest.TestCase):
    def test_is_array(self):
        cases = (
            ([1, 2], True),
            ((1, 2), True),
            (CustomSequence(1, 2), True),
            ("abc", False),
            (b"abc", False),
            (1, False),
            ({"a": 1}, False),
        )
        for case_input, expected in cases:
            self.assertIs(is_array(case_input), expected)

    def test_ensure_array_sequence_input(self):
        for obj in ([1, 2], (3, 4), CustomSequence(5, 6)):
            self.assertIs(ensure_array(obj), obj)

    def test_ensure_array_non_sequence_input(self):
        for obj in ("abc", b"abc", 1, {"a": 1}):
            self.assertListEqual(ensure_array(obj), [obj])
