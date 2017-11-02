
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
        actions = ['ec2:authorizesecuritygroupingress', 'iam:putrolepolicy', 'iam:listroles']
        groups = categories_for_actions(actions)
        self.assertIn('ec2', groups.keys())
        self.assertIn('iam', groups.keys())
        self.assertEqual(groups['ec2'], {'DataPlaneMutating'})
        self.assertEqual(groups['iam'], {u'Permissions', 'DataPlaneListRead'})

    def test_actions_for_category(self):
        from policyuniverse.action_categories import actions_for_category

        read_only_actions = actions_for_category('DataPlaneListRead')
        write_actions = actions_for_category('DataPlaneMutating')
        permission_actions = actions_for_category('Permissions')

        for action in permission_actions:
            self.assertFalse(':list' in action)
            self.assertFalse(':get' in action)

        for action in read_only_actions:
            # read actions shouldn't start with "Put" unless they are miscategorized.
            if action == 'ssm:putconfigurepackageresult':
                continue
            self.assertFalse(':put' in action)
            self.assertFalse(':create' in action)
            self.assertFalse(':attach' in action)

        for action in write_actions:
            # write actions shouldn't start with "get" unless they are miscategorized.
            if action in {'states:getactivitytask', 'glue:getmapping', 'cognito-identity:getid', 'ec2:describefpgaimages'}:
                continue
            print(action)
            self.assertFalse(':get' in action)
            self.assertFalse(':describe' in action)