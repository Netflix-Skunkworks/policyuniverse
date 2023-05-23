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
.. module: policyuniverse.tests.test_action_categories
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Patrick Kelley <patrick@netflix.com>

"""
import unittest


class ActionGroupTestCase(unittest.TestCase):
    def test_categories_for_actions(self):
        from policyuniverse.action_categories import categories_for_actions

        actions = [
            "ec2:authorizesecuritygroupingress",
            "iam:putrolepolicy",
            "iam:listroles",
        ]
        groups = categories_for_actions(actions)
        self.assertIn("ec2", groups.keys())
        self.assertIn("iam", groups.keys())
        self.assertEqual(groups["ec2"], {"Write"})
        self.assertEqual(groups["iam"], {"Permissions", "List"})

    def test_actions_for_category(self):
        from policyuniverse.action_categories import actions_for_category

        read_only_actions = actions_for_category("Read")
        list_only_actions = actions_for_category("List")
        write_actions = actions_for_category("Write")
        permission_actions = actions_for_category("Permissions")

        for action in permission_actions:
            if action in {
                "glue:getdatapreviewstatement",
                "glue:getnotebookinstancestatus",
                "imagebuilder:getcomponentpolicy",
                "imagebuilder:getimagepolicy",
                "imagebuilder:getimagerecipepolicy",
                "iotsitewise:listaccesspolicies",
                "managedblockchain:get",
                "monitron:listprojectadminusers",
                "signer:listprofilepermissions",
                "xray:getencryptionconfig",
            }:  # miscategorized AWS actions
                continue

            self.assertFalse(":list" in action, action)
            self.assertFalse(":get" in action, action)

        for action in list_only_actions:
            self.assertFalse(":put" in action, action)
            self.assertFalse(":create" in action, action)
            self.assertFalse(":attach" in action, action)

        for action in read_only_actions:
            # read actions shouldn't start with "Put" or "Create" unless they are miscategorized.
            if action in {
                "cloud9:createenvironmenttoken",
                "codeguru-reviewer:createconnectiontoken",
                "kinesisanalytics:createapplicationpresignedurl",
                "ssm:putconfigurepackageresult",
            }:  # miscategorized AWS actions
                continue
            # self.assertFalse(':list' in action)  # Tons of list* permissions are mis-categorized(?) as Read.
            self.assertFalse(":put" in action, action)
            self.assertFalse(":create" in action, action)
            self.assertFalse(":attach" in action, action)

        for action in write_actions:
            # write actions shouldn't start with "get" unless they are miscategorized.
            if action in {
                "appstream:getparametersforthemeassetupload",
                "backup-storage:describebackupjob",
                "backup-storage:getbasebackup",
                "backup-storage:getchunk",
                "backup-storage:getincrementalbasebackup",
                "backup-storage:getobjectmetadata",
                "bugbust:getjoineventstatus",
                "cloudshell:getfiledownloadurls",
                "cloudshell:getfileuploadurls",
                "cognito-identity:getid",
                "connect:getfederationtokens",
                "dataexchange:getjob",
                "elasticmapreduce:getclustersessioncredentials",
                "elasticmapreduce:getonclusterappuipresignedurl",
                "elasticmapreduce:getpersistentappuipresignedurl",
                "emr-containers:getmanagedendpointsessioncredentials",
                "glue:getmapping",
                "lakeformation:getdataaccess",
                "license-manager-linux-subscriptions:getservicesettings",
                "lightsail:getinstanceaccessdetails",
                "lightsail:getrelationaldatabasemasteruserpassword",
                "personalize:getpersonalizedranking",
                "quicksight:describecustompermissions",
                "redshift-serverless:getcredentials",
                "redshift:getclustercredentials",
                "redshift:getclustercredentialswithiam",
                "states:getactivitytask",
            }:  # miscategorized AWS actions
                continue
            self.assertFalse(":get" in action, action)
            self.assertFalse(":describe" in action, action)
