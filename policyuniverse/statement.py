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
.. module: policyuniverse.statement
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Patrick Kelley <patrickbarrettkelley@gmail.com> @patrickbkelley

"""
import re
from collections import namedtuple

from policyuniverse import logger
from policyuniverse.action_categories import categories_for_actions
from policyuniverse.arn import ARN
from policyuniverse.common import ensure_array, is_array
from policyuniverse.expander_minimizer import get_actions_from_statement

try:
    from collections.abc import Mapping
except ImportError:
    # Python 2.7 compatibility
    from collections import Mapping

PrincipalTuple = namedtuple("Principal", "category value")
ConditionTuple = namedtuple("Condition", "category value")


class Statement(object):
    def __init__(self, statement):
        self.statement = statement
        self.condition_entries = self._condition_entries()
        self.principals = self._principals()
        self.actions = self._actions()

    @property
    def effect(self):
        return self.statement.get("Effect")

    @property
    def actions_expanded(self):
        return set(get_actions_from_statement(self.statement))

    def _actions(self):
        actions = self.statement.get("Action")
        if not actions:
            return set()
        actions = ensure_array(actions)
        return set(actions)

    def action_summary(self):
        return categories_for_actions(self.actions_expanded)

    def uses_not_principal(self):
        return "NotPrincipal" in self.statement

    @property
    def resources(self):
        if "NotResource" in self.statement:
            return set(["*"])

        resources = ensure_array(self.statement.get("Resource"))
        return set(resources)

    def whos_allowed(self):
        """Returns set containing any entries from principal and condition section.

        Example:

        statement = Statement(dict(
            Effect='Allow',
            Principal='arn:aws:iam::*:role/Hello',
            Action=['ec2:*'],
            Resource='*',
            Condition={
                'StringLike': {
                    'AWS:SourceOwner': '012345678910'
                }}))

        statement.whos_allowed()
        > set([
        >    PrincipalTuple(category='principal', value='arn:aws:iam::*:role/Hello'),
        >    ConditionTuple(category='account', value='012345678910')])
        """
        who = set()
        for principal in self.principals:
            principal = PrincipalTuple(category="principal", value=principal)
            who.add(principal)
        who = who.union(self.condition_entries)
        return who

    def _principals(self):
        """Extracts all principals from IAM statement.

        Should handle these cases:
        "Principal": "value"
        "Principal": ["value"]
        "Principal": { "AWS": "value" }
        "Principal": { "AWS": ["value", "value"] }
        "Principal": { "Service": "value" }
        "Principal": { "Service": ["value", "value"] }

        Return: Set of principals
        """
        principals = set()
        principal = self.statement.get("Principal", None)
        if not principal:
            # It is possible not to define a principal, AWS ignores these statements.
            return principals

        if isinstance(principal, Mapping):

            if "AWS" in principal:
                self._add_or_extend(principal["AWS"], principals)

            if "Service" in principal:
                self._add_or_extend(principal["Service"], principals)

            if "Federated" in principal:
                self._add_or_extend(principal["Federated"], principals)

        else:
            self._add_or_extend(principal, principals)

        return principals

    def _add_or_extend(self, value, structure):
        if is_array(value):
            structure.update(set(value))
        else:
            structure.add(value)

    def _condition_entries(self):
        """Extracts any ARNs, Account Numbers, UserIDs, Usernames, CIDRs, VPCs, and VPC Endpoints from a condition block.

        Ignores any negated condition operators like StringNotLike.
        Ignores weak condition keys like referer, date, etc.

        Reason: A condition is meant to limit the principal in a statement.  Often, resource policies use a wildcard principal
        and rely exclusively on the Condition block to limit access.

        We would want to alert if the Condition had no limitations (like a non-existent Condition block), or very weak
        limitations.  Any negation would be weak, and largely equivelant to having no condition block whatsoever.

        The alerting code that relies on this data must ensure the condition has at least one of the following:
        - A limiting ARN
        - Account Identifier
        - AWS Organization Principal Org ID
        - User ID
        - Source IP / CIDR
        - VPC
        - VPC Endpoint

        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html
        """
        conditions = list()
        condition = self.statement.get("Condition")
        if not condition:
            return conditions

        key_mapping = {
            "aws:sourcearn": "arn",
            "aws:principalarn": "arn",
            "aws:sourceowner": "account",
            "aws:sourceaccount": "account",
            "aws:principalaccount": "account",
            "aws:principalorgid": "org-id",
            "kms:calleraccount": "account",
            "aws:userid": "userid",
            "aws:sourceip": "cidr",
            "aws:sourcevpc": "vpc",
            "aws:sourcevpce": "vpce",
            # a key for SAML Federation trust policy.
            # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_saml.html
            # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_saml_assertions.html
            "saml:aud": "saml-endpoint",
        }

        relevant_condition_operators = [
            re.compile(
                "((ForAllValues|ForAnyValue):)?ARN(Equals|Like)(IfExists)?",
                re.IGNORECASE,
            ),
            re.compile(
                "((ForAllValues|ForAnyValue):)?String(Equals|Like)(IgnoreCase)?(IfExists)?",
                re.IGNORECASE,
            ),
            re.compile(
                "((ForAllValues|ForAnyValue):)?IpAddress(IfExists)?", re.IGNORECASE
            ),
        ]

        for condition_operator in condition.keys():
            if any(
                regex.match(condition_operator)
                for regex in relevant_condition_operators
            ):
                for key, value in condition[condition_operator].items():

                    if key.lower() in key_mapping:
                        if is_array(value):
                            for v in value:
                                conditions.append(
                                    ConditionTuple(
                                        value=v, category=key_mapping[key.lower()]
                                    )
                                )
                        else:
                            conditions.append(
                                ConditionTuple(
                                    value=value, category=key_mapping[key.lower()]
                                )
                            )

        return conditions

    @property
    def condition_arns(self):
        return self._condition_field("arn")

    @property
    def condition_accounts(self):
        return self._condition_field("account")

    @property
    def condition_orgids(self):
        return self._condition_field("org-id")

    @property
    def condition_userids(self):
        return self._condition_field("userid")

    @property
    def condition_cidrs(self):
        return self._condition_field("cidr")

    @property
    def condition_vpcs(self):
        return self._condition_field("vpc")

    @property
    def condition_vpces(self):
        return self._condition_field("vpce")

    def _condition_field(self, field):
        return set(
            [entry.value for entry in self.condition_entries if entry.category == field]
        )

    def is_internet_accessible(self):
        if self.effect != "Allow":
            return False

        if not self.is_condition_internet_accessible():
            return False

        if self.uses_not_principal():
            return True

        for principal in self.principals:
            if self._arn_internet_accessible(principal):
                return True

        return False

    def is_condition_internet_accessible(self):
        condition_entries = self.condition_entries
        if len(condition_entries) == 0:
            return True

        for entry in condition_entries:
            if self._is_condition_entry_internet_accessible(entry):
                return True

        return False

    def _is_condition_entry_internet_accessible(self, entry):
        if entry.category == "arn":
            return self._arn_internet_accessible(entry.value)

        if entry.category == "userid":
            return self._userid_internet_accessible(entry.value)

        if entry.category == "cidr":
            return self._cidr_internet_accessible(entry.value)

        return "*" in entry.value

    def _cidr_internet_accessible(self, cidr):
        """The caller will want to inspect the CIDRs directly.
        This will only look for /0's.
        """
        return cidr.endswith("/0")

    def _userid_internet_accessible(self, userid):
        # Trailing wildcards are okay for userids:
        # AROAIIIIIIIIIIIIIIIII:*
        if userid.index("*") == len(userid) - 1:
            return False
        return True

    def _arn_internet_accessible(self, arn_input):
        if "*" == arn_input:
            return True

        arn = ARN(arn_input)
        if arn.error:
            logger.warning("Auditor could not parse ARN {arn}.".format(arn=arn_input))
            return "*" in arn_input

        if arn.tech == "s3":
            # S3 ARNs typically don't have account numbers.
            return False

        if not arn.account_number and not arn.service:
            logger.warning(
                "Auditor could not parse Account Number from ARN {arn}.".format(
                    arn=arn_input
                )
            )
            return True

        if arn.account_number == "*":
            return True

        return False
