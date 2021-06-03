#     Copyright 2015 Netflix, Inc.
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
.. module: policyuniverse.arn
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor:: Patrick Kelley <patrickbarrettkelley@gmail.com> @patrickbkelley

"""
import re

from policyuniverse import logger


class ARN(object):
    arn = None
    tech = None
    region = None
    account_number = None
    name = None
    partition = None
    error = False
    root = False
    service = False
    unique_id = None

    def __init__(self, input):
        self.arn = input
        arn_match = re.search(
            r"^arn:([^:]*):([^:]*):([^:]*):(|\*|[\d]{12}|cloudfront|aws):(.+)$", input
        )
        if arn_match:
            if arn_match.group(2) == "iam" and arn_match.group(5) == "root":
                self.root = True

            self._from_arn(arn_match, input)
            return

        acct_number_match = re.search(r"^(\d{12})+$", input)
        if acct_number_match:
            self._from_account_number(input)
            return

        aws_service_match = re.search(r"^(([^.]+)(.[^.]+)?)\.amazon(aws)?\.com$", input)
        if aws_service_match:
            self._from_aws_service(input, aws_service_match.group(1))
            return

        aws_service_match = re.search(r"^([^.]+).aws.internal$", input)
        if aws_service_match:
            self._from_aws_service(input, aws_service_match.group(1))
            return

        aws_service_match = re.search(
            r"^A(BI|CC|GP|ID|IP|KI|NP|NV|PK|RO|SC|SI)A", input
        )
        if aws_service_match:
            self._from_unique_id(input)
            return

        self.error = True
        logger.warning("ARN Could not parse [{}].".format(input))

    def _from_arn(self, arn_match, input):
        self.partition = arn_match.group(1)
        self.tech = arn_match.group(2)
        self.region = arn_match.group(3)
        self.account_number = arn_match.group(4)
        self.name = arn_match.group(5)

    def _from_account_number(self, input):
        self.account_number = input

    def _from_aws_service(self, input, service):
        self.tech = service
        self.service = True

    def _from_unique_id(self, input):
        self.unique_id = input
