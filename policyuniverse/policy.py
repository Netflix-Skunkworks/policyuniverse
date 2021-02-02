#     Copyright 2017 Netflix, Inc.
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
.. module: policyuniverse.policy
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Patrick Kelley <patrickbarrettkelley@gmail.com> @patrickbkelley

"""
from policyuniverse.statement import Statement
from policyuniverse.common import ensure_array
from collections import defaultdict


class Policy(object):
    def __init__(self, policy):
        self.policy = policy
        self.statements = []

        statement_structure = ensure_array(self.policy.get("Statement", []))

        for statement in statement_structure:
            self.statements.append(Statement(statement))

    @property
    def principals(self):
        principals = set()
        for statement in self.statements:
            principals = principals.union(statement.principals)
        return principals

    @property
    def condition_entries(self):
        condition_entries = set()
        for statement in self.statements:
            condition_entries = condition_entries.union(statement.condition_entries)
        return condition_entries

    def action_summary(self):
        action_categories = defaultdict(set)
        for statement in self.statements:
            for service, groups in statement.action_summary().items():
                action_categories[service] = action_categories[service].union(groups)
        return action_categories

    def is_internet_accessible(self):
        for statement in self.statements:
            if statement.is_internet_accessible():
                return True
        return False

    def internet_accessible_actions(self):
        actions = set()
        for statement in self.statements:
            if statement.is_internet_accessible():
                actions = actions.union(statement.actions)
        return actions

    def whos_allowed(self):
        allowed = set()
        for statement in self.statements:
            if statement.effect == "Allow":
                allowed = allowed.union(statement.whos_allowed())
        return allowed
