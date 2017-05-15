# PolicyUniverse

[![Version](http://img.shields.io/pypi/v/policyuniverse.svg?style=flat)](https://pypi.python.org/pypi/policyuniverse/)

[![Build Status](https://travis-ci.org/Netflix-Skunkworks/policyuniverse.svg?branch=master)](https://travis-ci.org/Netflix-Skunkworks/policyuniverse)

[![Coverage Status](https://coveralls.io/repos/github/Netflix-Skunkworks/policyuniverse/badge.svg?branch=master&1)](https://coveralls.io/github/Netflix-Skunkworks/policyuniverse?branch=master)

This package expands wildcards in AWS IAM Policies using permissions obtained from the AWS Policy Generator.

See the [list of all AWS permissions](policyuniverse/master_permissions.json).

_This package can also minify an AWS policy to help you stay under policy size limits. Avoid doing this if possible, as it creates ugly policies._ 💩

# Install:

`pip install policyuniverse`

# Usage:

```python
from policyuniverse import expand_policy
from policyuniverse import minimize_policy

policy = {
        "Statement": [{
            "Action": ["swf:res*"],
            "Resource": "*",
            "Effect": "Allow"
          }]
      }
      
expanded_policy = expand_policy(policy=policy)
>>> Start size: 131. End size: 286
print(expanded_policy == {
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
      })
>>> True

minimized_policy = minimize_policy(policy=expanded_policy, minchars=3)
>>> Skipping prefix r because length of 1
>>> Skipping prefix re because length of 2
>>> Skipping prefix r because length of 1
>>> Skipping prefix re because length of 2
>>> Skipping prefix r because length of 1
>>> Skipping prefix re because length of 2
>>> Skipping prefix r because length of 1
>>> Skipping prefix re because length of 2
>>> Start size: 286. End size: 131

print(minimized_policy == policy)
>>> True
```

