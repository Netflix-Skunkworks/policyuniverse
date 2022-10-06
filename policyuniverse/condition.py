#     Copyright 2022 Amazon.com, Inc.
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
.. module: policyuniverse.condition
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor:: Chris Partridge <chris@partridge.tech> @_tweedge

"""


class Condition(object):
    def __init__(self, location, key, category, value):
        self.location = location
        self.key = key
        self.category = category
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Condition):
            return NotImplemented

        return all(
            [
                self.location == other.location,
                self.key == other.key,
                self.category == other.category,
                self.value == other.value,
            ]
        )

    def __hash__(self):
        return hash(str(self.location) + self.key + self.category + self.value)

    def __repr__(self):
        return (
            "Condition: " + str(self.location) + self.key + self.category + self.value
        )
