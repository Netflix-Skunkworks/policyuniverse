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

try:
    from collections.abc import Sequence
except ImportError:
    # Python 2.7 compatibility
    from collections import Sequence

try:
    # Python 2.7 compatibility
    _STRING_TYPES = (bytes, str, unicode)
except NameError:
    _STRING_TYPES = (bytes, str)


def is_array(obj):
    """
    Check if the object is iterable, excluding strings:
    - tuple
    - list
    - collections.abc.Sequence sub-class
    """
    if isinstance(obj, _STRING_TYPES):
        return False
    return isinstance(obj, Sequence)


def ensure_array(obj):
    """
    Ensures that the given object is an array,
    by creating a list and adding it as a single element.
    """
    if is_array(obj):
        return obj
    else:
        return [obj]
