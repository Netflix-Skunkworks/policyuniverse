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
.. module: policyuniverse.tests.test_arn
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Mike Grima <mgrima@netflix.com>

"""
from policyuniverse.arn import ARN
from policyuniverse import logger
import unittest


class ARNTestCase(unittest.TestCase):
    def test_from_arn(self):
        proper_arns = [
            'events.amazonaws.com',
            'cloudtrail.amazonaws.com',
            'arn:aws:iam::012345678910:root',
            'arn:aws:iam::012345678910:role/SomeTestRoleForTesting',
            'arn:aws:iam::012345678910:instance-profile/SomeTestInstanceProfileForTesting',
            'arn:aws:iam::012345678910:role/*',
            'arn:aws:iam::012345678910:role/SomeTestRole*',
            'arn:aws:s3:::some-s3-bucket',
            'arn:aws:s3:*:*:some-s3-bucket',
            'arn:aws:s3:::some-s3-bucket/some/path/within/the/bucket'
            'arn:aws:s3:::some-s3-bucket/*',
            'arn:aws:ec2:us-west-2:012345678910:instance/*',
            'arn:aws:ec2:ap-northeast-1:012345678910:security-group/*',
            'arn:aws-cn:ec2:ap-northeast-1:012345678910:security-group/*',
            'arn:aws-us-gov:ec2:gov-west-1:012345678910:instance/*',
            'arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity EXXXXXXXXXXXXX'
        ]

        # Proper ARN Tests:
        for arn in proper_arns:
            logger.info('Testing Proper ARN: {}'.format(arn))
            arn_obj = ARN(arn)

            self.assertFalse(arn_obj.error)
            if "root" in arn:
                self.assertTrue(arn_obj.root)
            else:
                self.assertFalse(arn_obj.root)

            if ".amazonaws.com" in arn:
                self.assertTrue(arn_obj.service)
            else:
                self.assertFalse(arn_obj.service)

        bad_arns = [
            'arn:aws:iam::012345678910',
            'arn:aws:iam::012345678910:',
            '*',
            'arn:s3::::',
            "arn:arn:arn:arn:arn:arn"
        ]

        # Improper ARN Tests:
        for arn in bad_arns:
            logger.info('Testing IMPROPER ARN: {}'.format(arn))
            arn_obj = ARN(arn)

            self.assertTrue(arn_obj.error)

    def test_from_account_number(self):
        proper_account_numbers = [
            '012345678912',
            '123456789101',
            '123456789101'
        ]

        improper_account_numbers = [
            '*',
            'O12345678912',  # 'O' instead of '0'
            'asdfqwer',
            '123456',
            '89789456314356132168978945',
            '568947897*'
        ]

        # Proper account number tests:
        for accnt in proper_account_numbers:
            logger.info('Testing Proper Account Number: {}'.format(accnt))
            arn_obj = ARN(accnt)

            self.assertFalse(arn_obj.error)

        # Improper account number tests:
        for accnt in improper_account_numbers:
            logger.info('Testing IMPROPER Account Number: {}'.format(accnt))
            arn_obj = ARN(accnt)

            self.assertTrue(arn_obj.error)
