import unittest
from iampoliciesgonewild import expand_policy

WILDCARD_POLICY_1 = {
"Statement": [{
    "Action": ["swf:res*"],
    "Resource": "*",
    "Effect": "Allow"
  }]
}

EXPANDED_POLICY_1 = {
"Statement": [{
    "Action": [
      "swf:respondactivitytaskcanceled",
      "swf:respondactivitytaskcompleted",
      "swf:respondactivitytaskfailed",
      "swf:responddecisiontaskcompleted"
    ],
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

class TestMethods(unittest.TestCase):

  def test_expand_1(self):
      expanded_policy = expand_policy(policy=WILDCARD_POLICY_1)
      self.assertEqual(expanded_policy, EXPANDED_POLICY_1)

  def test_expand_2(self):
      expanded_policy = expand_policy(policy=WILDCARD_POLICY_2)
      self.assertEqual(expanded_policy, EXPANDED_POLICY_2)

if __name__ == '__main__':
    unittest.main()
