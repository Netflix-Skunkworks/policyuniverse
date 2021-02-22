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
.. module: policyuniverse.tests.test_policy
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Patrick Kelley <patrick@netflix.com>

"""
from policyuniverse.policy import Policy
from policyuniverse import logger
import unittest
import json

from .helpers import CustomMapping, CustomSequence


policy01 = dict(
    Version="2012-10-08",
    Statement=dict(
        Effect="Allow",
        Principal="*",
        Action=["rds:*"],
        Resource="*",
        Condition={"IpAddress": {"AWS:SourceIP": ["0.0.0.0/0"]}},
    ),
)

policy02 = dict(
    Version="2010-08-14",
    Statement=[
        dict(
            Effect="Allow",
            Principal="arn:aws:iam::012345678910:root",
            Action=["rds:*"],
            Resource="*",
        )
    ],
)

# One statement limits by ARN, the other allows any account number
policy03 = dict(
    Version="2010-08-14",
    Statement=[
        dict(
            Effect="Allow",
            Principal="arn:aws:iam::012345678910:root",
            Action=["s3:*"],
            Resource="*",
        ),
        dict(
            Effect="Allow",
            Principal="arn:aws:iam::*:role/Hello",
            Action=["ec2:*"],
            Resource="*",
        ),
    ],
)

# Two statements, one limited by account condition
policy04 = dict(
    Version="2010-08-14",
    Statement=[
        dict(
            Effect="Allow",
            Principal="arn:aws:iam::012345678910:root",
            Action=["s3:*"],
            Resource="*",
        ),
        dict(
            Effect="Allow",
            Principal="arn:aws:iam::*:role/Hello",
            Action=["ec2:*"],
            Resource="*",
            Condition={"StringLike": {"AWS:SourceOwner": "012345678910"}},
        ),
    ],
)

# Two statements, both with conditions
policy05 = dict(
    Version="2010-08-14",
    Statement=[
        dict(
            Effect="Allow",
            Principal="arn:aws:iam::012345678910:root",
            Action=["s3:*"],
            Resource="*",
            Condition={"IpAddress": {"AWS:SourceIP": ["0.0.0.0/0"]}},
        ),
        dict(
            Effect="Allow",
            Principal="arn:aws:iam::*:role/Hello",
            Action=["ec2:*"],
            Resource="*",
            Condition={"StringLike": {"AWS:SourceOwner": "012345678910"}},
        ),
    ],
)

# AWS Organizations
policy06 = dict(
    Version="2010-08-14",
    Statement=[
        dict(
            Effect="Allow",
            Principal="*",
            Action=["rds:*"],
            Resource="*",
            Condition={"StringEquals": {"AWS:PrincipalOrgID": "o-xxxxxxxxxx"}},
        )
    ],
)

# Custom types
policy07 = CustomMapping(
    dict(
        Statement=CustomSequence(
            [
                CustomMapping(
                    dict(
                        Action="s3:GetBucketAcl",
                        Effect="Allow",
                        Principal=CustomMapping({"AWS": "*"}),
                        Resource="arn:aws:s3:::example-bucket",
                        Sid="Public Access",
                    )
                )
            ]
        ),
        Version="2012-10-17",
    )
)


class PolicyTestCase(unittest.TestCase):
    def test_internet_accessible(self):
        self.assertTrue(Policy(policy01).is_internet_accessible())
        self.assertFalse(Policy(policy02).is_internet_accessible())
        self.assertTrue(Policy(policy03).is_internet_accessible())

    def test_internet_accessible_actions(self):
        self.assertEqual(Policy(policy01).internet_accessible_actions(), set(["rds:*"]))
        self.assertEqual(Policy(policy03).internet_accessible_actions(), set(["ec2:*"]))

    def test_action_summary(self):
        summary = Policy(policy05).action_summary()
        self.assertEqual(
            summary,
            {
                "ec2": {"List", "Write", "Read", "Tagging", "Permissions"},
                "s3": {"Write", "Read", "List", "Permissions", "Tagging"},
            },
        )

    def test_principals(self):
        self.assertEqual(
            Policy(policy04).principals,
            set(["arn:aws:iam::012345678910:root", "arn:aws:iam::*:role/Hello"]),
        )

    def test_condition_entries(self):
        from policyuniverse.statement import ConditionTuple

        self.assertEqual(
            Policy(policy05).condition_entries,
            set(
                [
                    ConditionTuple(category="cidr", value="0.0.0.0/0"),
                    ConditionTuple(category="account", value="012345678910"),
                ]
            ),
        )

        self.assertEqual(
            Policy(policy06).condition_entries,
            set([ConditionTuple(category="org-id", value="o-xxxxxxxxxx")]),
        )

    def test_whos_allowed(self):
        allowed = Policy(policy03).whos_allowed()
        self.assertEqual(len(allowed), 2)

        allowed = Policy(policy04).whos_allowed()
        self.assertEqual(len(allowed), 3)
        principal_allowed = set(
            [item for item in allowed if item.category == "principal"]
        )
        self.assertEqual(len(principal_allowed), 2)
        condition_account_allowed = set(
            [item for item in allowed if item.category == "account"]
        )
        self.assertEqual(len(condition_account_allowed), 1)

        allowed = Policy(policy06).whos_allowed()
        self.assertEqual(len(allowed), 2)

    def test_evasion_policies(self):
        """Some policies that may have been crafted to evade policycheckers."""
        S3_PUBLIC_BUCKET_POLICY = (
            '{"Version":"2008-10-17","Statement":['
            + "{"
            + '"Effect":"Allow","Principal":{"AWS":"*"},'
            + '"Action":["s3:GetObject","s3:GetObjectTorrent"],'
            + '"Resource":"arn:aws:s3:::%s/*",'
            + '"Condition":{"StringNotLike":{"aws:UserAgent":"|_(..)_|"},"NotIpAddress":{"aws:SourceIp":"8.8.8.8"}}'
            + "}"
            + "]}"
        )

        policy = Policy(json.loads(S3_PUBLIC_BUCKET_POLICY))
        self.assertTrue(policy.is_internet_accessible())

        S3_REPLICATION_DESTINATION_POLICY = (
            '{"Version":"2008-10-17","Statement":['
            + "{"
            + '"Effect":"Allow","Principal":{"AWS":"arn:aws:iam::%s:root"},'
            + '"Action":["s3:*"],"Resource":"arn:aws:s3:::%s/*"'
            + "},"
            + "{"
            + '"Effect":"Allow","Principal":{"AWS":"*"},'
            + '"Action":["s3:GetObject"],'
            + '"Resource":"arn:aws:s3:::%s/*",'
            + '"Condition":{"StringNotLike":{"aws:UserAgent": "|_(..)_|"},"NotIpAddress":{"aws:SourceIp":"8.8.8.8"}}'
            + "}"
            + "]}"
        )

        policy = Policy(json.loads(S3_REPLICATION_DESTINATION_POLICY))
        self.assertTrue(policy.is_internet_accessible())

        SQS_NOTIFICATION_POLICY = (
            '{"Version":"2008-10-17","Statement":['
            + "{"
            + '"Effect":"Allow","Principal":"*",'
            + '"Action":["SQS:ReceiveMessage","SQS:DeleteMessage"],'
            + '"Resource":"%s",'
            + '"Condition":{"StringNotLike":{"aws:UserAgent": "|_(..)_|"},"NotIpAddress":{"aws:SourceIp":"8.8.8.8"}}'
            + "},"
            + "{"
            + '"Effect":"Allow","Principal":{"AWS":"*"},'
            + '"Action":["SQS:SendMessage"],'
            + '"Resource":"%s",'
            + '"Condition":{"ArnLike":{"aws:SourceArn":"arn:aws:s3:*:*:%s"}}'
            + "}"
            + "]}"
        )

        policy = Policy(json.loads(SQS_NOTIFICATION_POLICY))
        self.assertTrue(policy.is_internet_accessible())

    def test_non_list_sequence_statement(self):
        policy_document = dict(
            Version="2012-10-08",
            Statement=(
                dict(
                    Effect="Allow",
                    Principal="*",
                    Action=["rds:*"],
                    Resource="*",
                    Condition={"IpAddress": {"AWS:SourceIP": ["0.0.0.0/0"]}},
                ),
            ),
        )
        policy = Policy(policy_document)
        self.assertTrue(policy.is_internet_accessible())
        self.assertListEqual(
            list(s.statement for s in policy.statements),
            [policy_document["Statement"][0]],
        )

    def test_mapping_and_sequence_policy_document(self):
        policy = Policy(policy07)
        self.assertSetEqual(policy.principals, set("*"))
        self.assertIs(policy.is_internet_accessible(), True)
