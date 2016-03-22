import unittest
from iampoliciesgonewild import expand_policy

WILDCARD_POLICY = {
"Statement": [{
    "Action": ["swf:res*"],
    "Resource": "*",
    "Effect": "Allow"
  }]
}

EXPANDED_POLICY = {
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

class TestMethods(unittest.TestCase):

  def test_expand(self):
      expanded_policy = expand_policy(policy=WILDCARD_POLICY)
      self.assertEqual(expanded_policy, EXPANDED_POLICY)

if __name__ == '__main__':
    unittest.main()