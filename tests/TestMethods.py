import unittest
import copy
from policyuniverse import expand_policy
from policyuniverse import minimize_policy
from policyuniverse import expand_minimize_over_policies
from policyuniverse import get_actions_from_statement
from policyuniverse import all_permissions
from policyuniverse import minimize_statement_actions
from policyuniverse import score_policy
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
  "autoscaling:describenotificationconfigurations",
  "autoscaling:deletetags",
  "autoscaling:describeterminationpolicytypes",
  "autoscaling:detachloadbalancers",
  "autoscaling:deletepolicy",
  "autoscaling:putscalingpolicy",
  "autoscaling:setinstanceprotection",
  "autoscaling:describescalingactivities",
  "autoscaling:createorupdatetags",
  "autoscaling:terminateinstanceinautoscalinggroup",
  "autoscaling:createlaunchconfiguration",
  "autoscaling:describeautoscalinginstances",
  "autoscaling:completelifecycleaction",
  "autoscaling:describetags",
  "autoscaling:describelifecyclehooks",
  "autoscaling:describeloadbalancers",
  "autoscaling:attachinstances",
  "autoscaling:describeadjustmenttypes",
  "autoscaling:recordlifecycleactionheartbeat",
  "autoscaling:putlifecyclehook",
  "autoscaling:describeautoscalingnotificationtypes",
  "autoscaling:executepolicy",
  "autoscaling:describeautoscalinggroups",
  "autoscaling:createautoscalinggroup",
  "autoscaling:describelaunchconfigurations",
  "autoscaling:enablemetricscollection",
  "autoscaling:putnotificationconfiguration",
  "autoscaling:setdesiredcapacity",
  "autoscaling:describescheduledactions",
  "autoscaling:attachloadbalancers",
  "autoscaling:deletescheduledaction",
  "autoscaling:disablemetricscollection",
  "autoscaling:describescalingprocesstypes",
  "autoscaling:deletelaunchconfiguration",
  "autoscaling:detachinstances",
  "autoscaling:deletenotificationconfiguration",
  "autoscaling:describeaccountlimits",
  "autoscaling:deleteautoscalinggroup",
  "autoscaling:deletelifecyclehook",
  "autoscaling:exitstandby",
  "autoscaling:setinstancehealth",
  "autoscaling:describelifecyclehooktypes",
  "autoscaling:suspendprocesses",
  "autoscaling:describemetriccollectiontypes",
  "autoscaling:putscheduledupdategroupaction",
  "autoscaling:describepolicies",
  "autoscaling:enterstandby",
  "autoscaling:resumeprocesses",
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

    def test_score_policy_controlplane_mutating(self):
        policy = {
            "Statement": [{
                "Action": ["iam:PutRolePolicy"],
                "Resource": "*",
                "Effect": "Allow"
            },{
                "Action": [
                    "s3:PutBucketPolicy",
                    "s3:PutBucketACL"
                    ],
                "Resource": "*",
                "Effect": "Allow"
            },{
                "Action": [
                    "sqs:SetQueueAttributes",
                    "sqs:AddPermission"
                    ],
                "Resource": "*",
                "Effect": "Allow"
            },{
                "Action": [
                    "sns:SetTopicAttributes",
                    "sns:AddPermission"
                    ],
                "Resource": "*",
                "Effect": "Allow"
            }]
        }
        score, service_tags, service_score = score_policy(policy)
        self.assertEqual(service_tags['iam'], {'CONTROL_PLANE', 'MUTATING'})
        self.assertEqual(service_score['iam'], 7)
        self.assertEqual(service_tags['s3'], {'CONTROL_PLANE', 'MUTATING'})
        self.assertEqual(service_score['s3'], 7)
        self.assertEqual(service_tags['sqs'], {'CONTROL_PLANE', 'MUTATING'})
        self.assertEqual(service_score['sqs'], 7)
        self.assertEqual(service_tags['sns'], {'CONTROL_PLANE', 'MUTATING'})
        self.assertEqual(service_score['sns'], 7)
        self.assertEqual(score, 47)


    def test_score_policy_dataplane_mutating(self):
        policy = {
            "Statement": [{
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectACL"
                    ],
                "Resource": "*",
                "Effect": "Allow"
            },{
                "Action": [
                    "sqs:SendMessage"
                    ],
                "Resource": "*",
                "Effect": "Allow"
            },{
                "Action": [
                    "sns:Publish"
                    ],
                "Resource": "*",
                "Effect": "Allow"
            },{
                "Action": [
                    "iam:ListRoles",
                    ],
                "Resource": "*",
                "Effect": "Allow"
            }]
        }
        score, service_tags, service_score = score_policy(policy)
        self.assertEqual(service_tags['s3'], {'DATA_PLANE', 'MUTATING'})
        self.assertEqual(service_score['s3'], 6)
        self.assertEqual(service_tags['sqs'], {'DATA_PLANE', 'SIDE_EFFECT'})
        self.assertEqual(service_score['sqs'], 5)
        self.assertEqual(service_tags['sns'], {'DATA_PLANE', 'SIDE_EFFECT'})
        self.assertEqual(service_score['sns'], 5)
        self.assertEqual(service_tags['iam'], {'READ'})
        self.assertEqual(service_score['iam'], 1)
        self.assertEqual(score, 23)


if __name__ == '__main__':
    unittest.main()
