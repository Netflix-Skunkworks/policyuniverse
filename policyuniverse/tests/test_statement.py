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
.. module: policyuniverse.tests.test_statement
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Patrick Kelley <pkelley@netflix.com>

"""
from policyuniverse.statement import Statement
import unittest

# NotPrincipal
statement01 = dict(
    Effect='Allow',
    NotPrincipal={'AWS': ['arn:aws:iam::012345678910:root']},
    Action=['rds:*'],
    Resource='*')

# "Principal": "value"
statement02 = dict(
    Effect='Allow',
    Principal='arn:aws:iam::012345678910:root',
    Action=['rds:*'],
    Resource='*')

# "Principal": { "AWS": "value" }
statement03 = dict(
    Effect='Allow',
    Principal={'AWS': 'arn:aws:iam::012345678910:root'},
    Action=['rds:*'],
    Resource='*')

# "Principal": { "AWS": ["value", "value"] }
statement04 = dict(
    Effect='Allow',
    Principal={'AWS': ['arn:aws:iam::012345678910:root']},
    Action=['rds:*'],
    Resource='*')

# "Principal": { "Service": "value", "AWS": "value" }
statement05 = dict(
    Effect='Allow',
    Principal={'Service': 'lambda.amazonaws.com', 'AWS': 'arn:aws:iam::012345678910:root'},
    Action=['rds:*'],
    Resource='*')

# "Principal": { "Service": ["value", "value"] }
statement06 = dict(
    Effect='Allow',
    Principal={'Service': ['lambda.amazonaws.com']},
    Action=['rds:*'],
    Resource='*')

statement07 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'ForAllValues:ARNEqualsIfExists': {
            'AWS:SourceArn': 'arn:aws:iam::012345678910:role/SomeTestRoleForTesting'
        }})

statement08 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'ForAnyValue:ARNEquals': {
            'AWS:SourceArn': [
                'arn:aws:iam::012345678910:role/SomeTestRoleForTesting',
                'arn:aws:iam::012345678910:role/OtherRole']
        }})

statement09 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringLike': {
            'AWS:SourceOwner': '012345678910'
        }})

statement09_wildcard = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringLike': {
            'AWS:SourceOwner': '*'
        }})

statement10 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'ForAnyValue:StringEquals': {
            'AWS:SourceOwner': '012345678910',
            'AWS:SourceAccount': '123456789123'
        }})

statement11 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'ForAnyValue:StringEquals': {
            'AWS:SourceOwner': ['012345678910', '123456789123']
        }})

statement12 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringEquals': {
            'AWS:SourceVPC': 'vpc-111111',
            'AWS:Sourcevpce': 'vpce-111111',
            'AWS:username': 'Admin',
            'AWS:SourceOwner': '012345678910',
            'AWS:SourceAccount': '012345678910'
        },
        'StringLike': {
            'AWS:userid': 'AROAI1111111111111111:*'
        },
        'ARNLike': {
            'AWS:SourceArn': 'arn:aws:iam::012345678910:role/Admin'
        },
        'IpAddressIfExists': {
            'AWS:SourceIP': [
                '123.45.67.89',
                '10.0.7.0/24',
                '172.16.0.0/16']
        }
    })

statement13 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringNotLike': {
            'AWS:userid': 'AROAI1111111111111111:*'
        },
        'ARNLike': {
            'AWS:SourceArn': 'arn:aws:iam::012345678910:role/Admin'
        }
    })

statement14 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*')

statement15 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringNotLike': {
            'AWS:userid': 'AROAI1111111111111111:*'
        }
    })

statement16 = dict(
    Effect='Deny',
    Principal='*',
    Action=['rds:*'],
    Resource='*')

# Bad ARN
statement17 = dict(
    Effect='Allow',
    Principal='arn:aws:iam::012345678910',
    Action=['rds:*'],
    Resource='*')

# ARN Like with wildcard account number
statement18 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'ARNLike': {
            'AWS:SourceArn': 'arn:aws:iam::*:role/Admin'
        }
    })

# StringLike with wildcard
statement19 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringLike': {
            'AWS:SourceArn': 'arn:aws:iam::*'
        }
    })

# Open CIDR
statement20 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'IpAddress': {
            'AWS:SourceIP': ['0.0.0.0/0']
        }
    })

# S3 ARN
statement21 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringEquals': {
            'AWS:SourceArn': 'arn:aws:s3:::mybucket'
        }})

# ARN without account number
statement22 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringEquals': {
            'AWS:SourceArn': 'arn:aws:iam:::user/MyUser'
        }})

# KMS decided to use their own Condition Keys:
statement23 = dict(
    Effect='Allow',
    Principal='*',
    Action=['kms:*'],
    Resource='*',
    Condition={
            "StringEquals": {
              "kms:ViaService": "lightsail.us-east-1.amazonaws.com",
              "kms:CallerAccount": "222222222222"
            }
          })

# Testing action groups
statement24 = dict(
    Effect='Allow',
    Principal='*',
    Action=['ec2:authorizesecuritygroupingress', 'ec2:AuthorizeSecuritygroupEgress'],
    Resource='*')

# Testing action groups
statement25 = dict(
    Effect='Allow',
    Principal='*',
    Action=['ec2:authorizesecuritygroupingress', 'ec2:AuthorizeSecuritygroupEgress', 'iam:putrolepolicy'],
    Resource='*')

# Testing action groups
statement26 = dict(
    Effect='Allow',
    Principal='*',
    Action=['iam:putrolepolicy', 'iam:listroles'],
    Resource='*')


class StatementTestCase(unittest.TestCase):
    def test_statement_effect(self):
        statement = Statement(statement01)
        self.assertEqual(statement.effect, 'Allow')

    def test_statement_not_principal(self):
        statement = Statement(statement01)
        self.assertTrue(statement.uses_not_principal())

    def test_statement_summary(self):
        statement = Statement(statement24)
        self.assertEqual(statement.action_summary(), {'ec2': {'DataPlaneMutating'}})

        statement = Statement(statement25)
        self.assertEqual(statement.action_summary(), {'ec2': {'DataPlaneMutating'}, 'iam': {'Permissions'}})

        statement = Statement(statement26)
        self.assertEqual(statement.action_summary(), {'iam': {'Permissions', 'DataPlaneListRead'}})

    def test_statement_principals(self):
        statement = Statement(statement02)
        self.assertEqual(statement.principals, set(['arn:aws:iam::012345678910:root']))

        statement = Statement(statement03)
        self.assertEqual(statement.principals, set(['arn:aws:iam::012345678910:root']))

        statement = Statement(statement04)
        self.assertEqual(statement.principals, set(['arn:aws:iam::012345678910:root']))

        statement = Statement(statement05)
        self.assertEqual(statement.principals, set(['arn:aws:iam::012345678910:root', 'lambda.amazonaws.com']))

        statement = Statement(statement06)
        self.assertEqual(statement.principals, set(['lambda.amazonaws.com']))

        statement_wo_principal = dict(statement06)
        del statement_wo_principal['Principal']
        statement = Statement(statement_wo_principal)
        self.assertEqual(statement.principals, set([]))

    def test_statement_conditions(self):
        statement = Statement(statement07)
        self.assertEqual(statement.condition_arns, set(['arn:aws:iam::012345678910:role/SomeTestRoleForTesting']))

        statement = Statement(statement08)
        self.assertEqual(statement.condition_arns,
            set(['arn:aws:iam::012345678910:role/SomeTestRoleForTesting',
            'arn:aws:iam::012345678910:role/OtherRole']))

        statement = Statement(statement10)
        self.assertEqual(statement.condition_accounts, set(['012345678910', '123456789123']))

        statement = Statement(statement11)
        self.assertEqual(statement.condition_accounts, set(['012345678910', '123456789123']))

        statement = Statement(statement12)
        self.assertEqual(statement.condition_arns, set(['arn:aws:iam::012345678910:role/Admin']))
        self.assertEqual(statement.condition_accounts, set(['012345678910']))
        self.assertEqual(statement.condition_userids, set(['AROAI1111111111111111:*']))
        self.assertEqual(statement.condition_cidrs, set(['123.45.67.89', '10.0.7.0/24', '172.16.0.0/16']))
        self.assertEqual(statement.condition_vpcs, set(['vpc-111111']))
        self.assertEqual(statement.condition_vpces, set(['vpce-111111']))

        statement = Statement(statement13)
        self.assertEqual(statement.condition_arns, set(['arn:aws:iam::012345678910:role/Admin']))
        self.assertEqual(len(statement.condition_userids), 0)

        statement = Statement(statement23)
        self.assertEqual(statement.condition_accounts, set(['222222222222']))

    def test_statement_internet_accessible(self):
        self.assertTrue(Statement(statement14).is_internet_accessible())
        self.assertTrue(Statement(statement15).is_internet_accessible())
        self.assertTrue(Statement(statement01).is_internet_accessible())

        self.assertFalse(Statement(statement02).is_internet_accessible())
        self.assertFalse(Statement(statement03).is_internet_accessible())
        self.assertFalse(Statement(statement04).is_internet_accessible())
        self.assertFalse(Statement(statement05).is_internet_accessible())
        self.assertFalse(Statement(statement06).is_internet_accessible())
        self.assertFalse(Statement(statement07).is_internet_accessible())
        self.assertFalse(Statement(statement08).is_internet_accessible())
        self.assertFalse(Statement(statement09).is_internet_accessible())
        self.assertTrue(Statement(statement09_wildcard).is_internet_accessible())
        self.assertFalse(Statement(statement10).is_internet_accessible())
        self.assertFalse(Statement(statement11).is_internet_accessible())
        self.assertFalse(Statement(statement12).is_internet_accessible())
        self.assertFalse(Statement(statement13).is_internet_accessible())
        self.assertTrue(Statement(statement14).is_internet_accessible())
        self.assertTrue(Statement(statement15).is_internet_accessible())

        self.assertFalse(Statement(statement16).is_internet_accessible())
        self.assertFalse(Statement(statement17).is_internet_accessible())

        self.assertTrue(Statement(statement18).is_internet_accessible())
        self.assertTrue(Statement(statement19).is_internet_accessible())
        self.assertTrue(Statement(statement20).is_internet_accessible())

        # Statements with ARNS lacking account numbers
        # 21 is an S3 ARN
        self.assertFalse(Statement(statement21).is_internet_accessible())
        # 22 is a likely malformed user ARN, but lacking an account number
        self.assertTrue(Statement(statement22).is_internet_accessible())
