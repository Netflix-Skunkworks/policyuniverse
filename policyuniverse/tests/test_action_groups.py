
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
.. module: policyuniverse.tests.test_action_groups
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Patrick Kelley <patrick@netflix.com>

"""
import unittest


class ActionGroupTestCase(unittest.TestCase):
    def test_groups_for_actions(self):
        from policyuniverse.action_groups import groups_for_actions
        actions = ['ec2:authorizesecuritygroupingress', 'iam:putrolepolicy', 'iam:listroles']
        groups = groups_for_actions(actions)
        self.assertIn('ec2', groups.keys())
        self.assertIn('iam', groups.keys())
        self.assertEqual(groups['ec2'], {'ReadWrite'})
        self.assertEqual(groups['iam'], {u'Permissions', u'ListOnly', u'ReadOnly', u'ReadWrite'})

        actions = ['iam:putrolepolicy']
        groups = groups_for_actions(actions)
        self.assertEqual(groups['iam'], {u'Permissions'})

    def test_actions_for_groups(self):
        from policyuniverse.action_groups import actions_for_groups
        
        # Permission actions are never ReadWrite actions.
        groups = ['Permissions', 'ReadWrite']
        self.assertEqual(0, len(actions_for_groups(groups)))

        # ReadWrite indicates a data plane operation.
        # All ReadOnly or ListOnly permissions also have ReadWrite
        read_only_actions = actions_for_groups(['ReadOnly'])
        list_only_actions = actions_for_groups(['ListOnly'])
        data_actions = actions_for_groups(['ReadWrite'])

        # The < sign for sets means proper-subset
        self.assertTrue(read_only_actions < data_actions)
        self.assertTrue(list_only_actions < data_actions)

        # All ListOnly permissions are also ReadOnly
        self.assertTrue(list_only_actions < read_only_actions)
