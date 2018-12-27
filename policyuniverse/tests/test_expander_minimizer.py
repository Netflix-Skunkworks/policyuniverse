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
.. module: policyuniverse.tests.test_expander_minimizer
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Mike Grima <mgrima@netflix.com>

"""
import unittest
import copy
from policyuniverse import expand_policy
from policyuniverse import minimize_policy
from policyuniverse import expand_minimize_over_policies
from policyuniverse import get_actions_from_statement
from policyuniverse import all_permissions
from policyuniverse import minimize_statement_actions
from policyuniverse import _get_prefixes_for_action
from policyuniverse import _expand_wildcard_action
from policyuniverse import _get_desired_actions_from_statement


WILDCARD_ACTION_1 = "swf:res*"

WILDCARD_POLICY_1 = {
"Statement": [{
    "Action": [WILDCARD_ACTION_1],
    "Resource": "*",
    "Effect": "Allow"
  }]
}

EXPANDED_ACTIONS_1 = ["swf:respondactivitytaskcanceled",
  "swf:respondactivitytaskcompleted",
  "swf:respondactivitytaskfailed",
  "swf:responddecisiontaskcompleted"]

EXPANDED_POLICY_1 = {
"Statement": [{
    "Action": EXPANDED_ACTIONS_1,
    "Resource": "*",
    "Effect": "Allow"
  }]
}

WILDCARD_POLICY_2 = {
"Statement": [{
    "Action": ["swf:*activitytaskc*"],
    "Resource": "*",
    "Effect": "Allow"
  }]
}

EXPANDED_POLICY_2 = {
"Statement": [{
    "Action": [
      "swf:respondactivitytaskcanceled",
      "swf:respondactivitytaskcompleted"
    ],
    "Resource": "*",
    "Effect": "Allow"
  }]
}

POLICIES_1 = {
    'policy': {
        'policyname1': WILDCARD_POLICY_1,
        'policyname2': WILDCARD_POLICY_2
    }
}

EXPANDED_POLICIES_1 = {
    'policy': {
        'policyname1': EXPANDED_POLICY_1,
        'policyname2': EXPANDED_POLICY_2
    }
}

AUTOSCALING_PERMISSIONS = sorted([
  "autoscaling:attachinstances",
  "autoscaling:attachloadbalancertargetgroups",
  "autoscaling:attachloadbalancers",
  "autoscaling:batchdeletescheduledaction",
  "autoscaling:batchputscheduledupdategroupaction",
  "autoscaling:completelifecycleaction",
  "autoscaling:createautoscalinggroup",
  "autoscaling:createlaunchconfiguration",
  "autoscaling:createorupdatetags",
  "autoscaling:deleteautoscalinggroup",
  "autoscaling:deletelaunchconfiguration",
  "autoscaling:deletelifecyclehook",
  "autoscaling:deletenotificationconfiguration",
  "autoscaling:deletepolicy",
  "autoscaling:deletescheduledaction",
  "autoscaling:deletetags",
  "autoscaling:describeaccountlimits",
  "autoscaling:describeadjustmenttypes",
  "autoscaling:describeautoscalinggroups",
  "autoscaling:describeautoscalinginstances",
  "autoscaling:describeautoscalingnotificationtypes",
  "autoscaling:describelaunchconfigurations",
  "autoscaling:describelifecyclehooktypes",
  "autoscaling:describelifecyclehooks",
  "autoscaling:describeloadbalancertargetgroups",
  "autoscaling:describeloadbalancers",
  "autoscaling:describemetriccollectiontypes",
  "autoscaling:describenotificationconfigurations",
  "autoscaling:describepolicies",
  "autoscaling:describescalingactivities",
  "autoscaling:describescalingprocesstypes",
  "autoscaling:describescheduledactions",
  "autoscaling:describetags",
  "autoscaling:describeterminationpolicytypes",
  "autoscaling:detachinstances",
  "autoscaling:detachloadbalancertargetgroups",
  "autoscaling:detachloadbalancers",
  "autoscaling:disablemetricscollection",
  "autoscaling:enablemetricscollection",
  "autoscaling:enterstandby",
  "autoscaling:executepolicy",
  "autoscaling:exitstandby",
  "autoscaling:putlifecyclehook",
  "autoscaling:putnotificationconfiguration",
  "autoscaling:putscalingpolicy",
  "autoscaling:putscheduledupdategroupaction",
  "autoscaling:recordlifecycleactionheartbeat",
  "autoscaling:resumeprocesses",
  "autoscaling:setdesiredcapacity",
  "autoscaling:setinstancehealth",
  "autoscaling:setinstanceprotection",
  "autoscaling:suspendprocesses",
  "autoscaling:terminateinstanceinautoscalinggroup",
  "autoscaling:updateautoscalinggroup"
])


def dc(o):
    """
    Some of the testing methods modify the datastructure you pass into them.
    We want to deepcopy each structure so one test doesn't break another.
    """
    return copy.deepcopy(o)


class TestMethods(unittest.TestCase):

    def test_expand_1(self):
        expanded_policy = expand_policy(policy=dc(WILDCARD_POLICY_1))
        self.assertEqual(expanded_policy, EXPANDED_POLICY_1)
        policy = {
            "Statement": {
                "NotAction": ["ec2:thispermissiondoesntexist"],
                "Resource": "*",
                "Effect": "Deny"
            }
        }
        expected_policy = {
            "Statement": [{
                "NotAction": ["ec2:thispermissiondoesntexist"],
                "Resource": "*",
                "Effect": "Deny"
            }]
        }
        expanded_policy = expand_policy(policy=dc(policy), expand_deny=False)
        self.assertEqual(expanded_policy, expected_policy)
        expanded_policy = expand_policy(policy=dc(policy), expand_deny=True)
        self.assertEqual(type(expanded_policy['Statement']), list)

    def test_expand_2(self):
        expanded_policy = expand_policy(policy=dc(WILDCARD_POLICY_2))
        self.assertEqual(expanded_policy, EXPANDED_POLICY_2)

    def test_expand_minimize_over_policies(self):
        result = expand_minimize_over_policies(dc(POLICIES_1), expand_policy)
        self.assertEqual(result, EXPANDED_POLICIES_1)

    def test_expand_minimize_over_policies_1(self):
        result = expand_minimize_over_policies(EXPANDED_POLICY_1, minimize_policy, minchars=3)
        self.assertEqual(result, WILDCARD_POLICY_1)

    def test_get_prefixes_for_action(self):
        result = _get_prefixes_for_action('iam:cat')
        self.assertEqual(result, ['iam:', 'iam:c', 'iam:ca', 'iam:cat'])

    def test_expand_wildcard_action(self):
        result = _expand_wildcard_action(['autoscaling:*'])
        self.assertEqual(sorted(result), AUTOSCALING_PERMISSIONS)

    def test_expand_wildcard_action_2(self):
        result = _expand_wildcard_action('thistechdoesntexist:*')
        self.assertEqual(result, ['thistechdoesntexist:*'])

    def test_expand_wildcard_action_3(self):
        result = _expand_wildcard_action('ec2:DescribeInstances')
        self.assertEqual(result, ['ec2:describeinstances'])

    def test_get_desired_actions_from_statement(self):
        result = _get_desired_actions_from_statement(dc(WILDCARD_POLICY_1['Statement'][0]))
        self.assertEqual(result, set(EXPANDED_ACTIONS_1))

    def test_get_desired_actions_from_statement_1(self):
        statement = {
            "Action": ["ec2:thispermissiondoesntexist"],
            "Resource": "*",
            "Effect": "Allow"
        }
        self.assertRaises(Exception, _get_desired_actions_from_statement, statement)

    def test_get_actions_from_statement(self):
        statement = {
            "Action": "ec2:thispermissiondoesntexist",
            "NotAction": list(all_permissions),
            "Resource": "*",
            "Effect": "Allow"
        }
        expected_result = {"ec2:thispermissiondoesntexist"}
        result = get_actions_from_statement(statement)
        self.assertEqual(result, expected_result)
        get_actions_from_statement(dict(NotAction="abc"))

    def test_minimize_statement_actions(self):
        statement = dict(Effect="Deny")
        self.assertRaises(Exception, minimize_statement_actions, statement)
