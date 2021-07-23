#     Copyright 2021 Amazon.com, Inc.
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
.. module: policyuniverse.tests.test_organization
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor:: Chris Partridge <chris@partridge.tech> @_tweedge

"""
import unittest

from policyuniverse import logger
from policyuniverse.organization import Organization


class OrganizationTestCase(unittest.TestCase):
    def test_from_org_id(self):
        # test valid organization IDs
        valid_org_ids = ["o-a1b2c3d4e5", "o-*", "*"]

        for org_id in valid_org_ids:
            logger.info("Testing valid organization ID: {}".format(org_id))
            organization_obj = Organization(org_id)

            self.assertFalse(organization_obj.error)
            self.assertEqual(org_id, organization_obj.organization)

        # test invalid organization IDs
        invalid_org_ids = [
            "o*",
            "r-*/ou-a1s2d3f4g5",
            "/o-*",
            "r-ab12",
            "ou-22222222",
        ]

        for org_id in invalid_org_ids:
            logger.info("Testing invalid organization ID: {}".format(org_id))
            organization_obj = Organization(org_id)

            self.assertTrue(organization_obj.error)

    def test_from_org_path(self):
        # test valid organization paths
        valid_org_paths = [
            "o-a1b2c3d4e5/*",
            "o-a1b2c3d4e5/*/ou-ab12-22222222",
            "o-a1b2c3d4e5/r-*/ou-*",
            "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111",
            "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/",
            "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/*",
            "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/ou-*",
            "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/ou-ab12-33333333/ou-*",
            "*/*",
            "*/*/*",
        ]

        for org_path in valid_org_paths:
            logger.info("Testing valid organization path: {}".format(org_path))
            organization_obj = Organization(org_path)

            self.assertFalse(organization_obj.error)

        # test invalid organization paths
        invalid_org_paths = [
            "dynamodb.amazonaws.com",
            "arn:aws:kms:region:111122223333:key/my-example-key",
            "111122223333",
            "arn:aws:s3:::some-s3-bucket",
            "arn:aws:iam::aws:policy/AlexaForBusinessDeviceSetup",
            "o-a1b2c3d4e5/*/*/*/*",
            "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-*/ou-*",
            "o-a1b2c3d4e5/o-a1b2c3d4e5/r-ab12/ou-22222222",
            "ou-a1b2c3d4e5/r-ab12/ou-22222222",
            "*/*/*/*",
            "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/ou-ab12-33333333/o-*",
            "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/ou-ab12-33333333/r-*",
        ]

        for org_path in invalid_org_paths:
            logger.info("Testing invalid organization path: {}".format(org_path))
            organization_obj = Organization(org_path)

            self.assertTrue(organization_obj.error)

    def test_parent_and_child_validity(self):
        # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-principalorgpaths
        # Source of test cases and explanation

        org_path = "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/"
        logger.info("Testing parent:true/child:false case {}".format(org_path))
        organization_obj = Organization(org_path)
        self.assertTrue(organization_obj.valid_for_parent_ou)
        self.assertFalse(organization_obj.valid_for_child_ous)

        org_path = "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/*"
        logger.info("Testing parent:true/child:true case {}".format(org_path))
        organization_obj = Organization(org_path)
        self.assertTrue(organization_obj.valid_for_parent_ou)
        self.assertTrue(organization_obj.valid_for_child_ous)

        org_path = "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/ou-*"
        logger.info("Testing parent:false/child:true case {}".format(org_path))
        organization_obj = Organization(org_path)
        self.assertFalse(organization_obj.valid_for_parent_ou)
        self.assertTrue(organization_obj.valid_for_child_ous)

        # show false/false as there is neither parent nor child
        org_path = "o-a1b2c3d4e5/*"
        logger.info("Testing parent:false/child:false case {}".format(org_path))
        organization_obj = Organization(org_path)
        self.assertFalse(organization_obj.valid_for_parent_ou)
        self.assertFalse(organization_obj.valid_for_child_ous)

    def test_root_toggles_child_validity_in_path(self):
        # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-principalorgpaths
        # If an orgpath is given with a root of *, any OU regardless of parent
        # can access the resource, so long as it is in the organization.
        # The same can be said of Organizations, from my understanding.
        # However, once an OU is given, OU-based restrictions apply.

        org_path = "o-a1b2c3d4e5"
        logger.info("Testing path without root: {}".format(org_path))
        organization_obj = Organization(org_path)
        self.assertTrue(organization_obj.valid_for_all_ous)

        org_path = "o-a1b2c3d4e5/*"
        logger.info("Testing path with root *: {}".format(org_path))
        organization_obj = Organization(org_path)
        self.assertTrue(organization_obj.valid_for_all_ous)

        org_path = "o-a1b2c3d4e5/*/ou-ab12-22222222"
        logger.info("Testing path with root * and trailing path: {}".format(org_path))
        organization_obj = Organization(org_path)
        self.assertFalse(organization_obj.valid_for_all_ous)
