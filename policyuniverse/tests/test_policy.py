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


policy01 = dict(
    Version='2012-10-08',
    Statement=dict(
        Effect='Allow',
        Principal='*',
        Action=['rds:*'],
        Resource='*',
        Condition={
            'IpAddress': {
                'AWS:SourceIP': ['0.0.0.0/0']
            }
        }))

policy02 = dict(
    Version='2010-08-14',
    Statement=[
        dict(Effect='Allow',
        Principal='arn:aws:iam::012345678910:root',
        Action=['rds:*'],
        Resource='*')])

# One statement limits by ARN, the other allows any account number
policy03 = dict(
    Version='2010-08-14',
    Statement=[
        dict(
            Effect='Allow',
            Principal='arn:aws:iam::012345678910:root',
            Action=['s3:*'],
            Resource='*'),
        dict(
            Effect='Allow',
            Principal='arn:aws:iam::*:role/Hello',
            Action=['ec2:*'],
            Resource='*'),
        ])

# Two statements, one limited by account condition
policy04 = dict(
    Version='2010-08-14',
    Statement=[
        dict(
            Effect='Allow',
            Principal='arn:aws:iam::012345678910:root',
            Action=['s3:*'],
            Resource='*'),
        dict(
            Effect='Allow',
            Principal='arn:aws:iam::*:role/Hello',
            Action=['ec2:*'],
            Resource='*',
            Condition={
                'StringLike': {
                    'AWS:SourceOwner': '012345678910'
                }})
        ])

# Two statements, both with conditions
policy05 = dict(
    Version='2010-08-14',
    Statement=[
        dict(
            Effect='Allow',
            Principal='arn:aws:iam::012345678910:root',
            Action=['s3:*'],
            Resource='*',
            Condition={
                'IpAddress': {
                    'AWS:SourceIP': ['0.0.0.0/0']
                }}),
        dict(
            Effect='Allow',
            Principal='arn:aws:iam::*:role/Hello',
            Action=['ec2:*'],
            Resource='*',
            Condition={
                'StringLike': {
                    'AWS:SourceOwner': '012345678910'
                }})
        ])

class PolicyTestCase(unittest.TestCase):
    def test_internet_accessible(self):
        self.assertTrue(Policy(policy01).is_internet_accessible())
        self.assertFalse(Policy(policy02).is_internet_accessible())
        self.assertTrue(Policy(policy03).is_internet_accessible())

    def test_internet_accessible_actions(self):
        self.assertEquals(
            Policy(policy01).internet_accessible_actions(),
            set(['rds:*']))
        self.assertEquals(
            Policy(policy03).internet_accessible_actions(),
            set(['ec2:*']))

    def test_principals(self):
        self.assertEquals(
            Policy(policy04).principals,
            set(['arn:aws:iam::012345678910:root', 'arn:aws:iam::*:role/Hello']))

    def test_condition_entries(self):
        from policyuniverse.statement import ConditionTuple
        self.assertEquals(
            Policy(policy05).condition_entries,
            set([
                ConditionTuple(category='cidr', value='0.0.0.0/0'),
                ConditionTuple(category='account', value='012345678910')
            ]))

    def test_whos_allowed(self):
        allowed = Policy(policy03).whos_allowed()
        self.assertEquals(len(allowed), 2)

        allowed = Policy(policy04).whos_allowed()
        self.assertEquals(len(allowed), 3)
        principal_allowed = set([item for item in allowed if item.category == 'principal'])
        self.assertEquals(len(principal_allowed), 2)
        condition_account_allowed = set([item for item in allowed if item.category == 'account'])
        self.assertEquals(len(condition_account_allowed), 1)