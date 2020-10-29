# PolicyUniverse

[![Version](http://img.shields.io/pypi/v/policyuniverse.svg?style=flat)](https://pypi.python.org/pypi/policyuniverse/)

[![Build Status](https://travis-ci.com/Netflix-Skunkworks/policyuniverse.svg?branch=master)](https://travis-ci.com/Netflix-Skunkworks/policyuniverse)

[![Coverage Status](https://coveralls.io/repos/github/Netflix-Skunkworks/policyuniverse/badge.svg?branch=master&1)](https://coveralls.io/github/Netflix-Skunkworks/policyuniverse?branch=master)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

This package provides classes to parse AWS IAM and Resource Policies.

Additionally, this package can expand wildcards in AWS Policies using permissions obtained from the AWS Policy Generator.

See the [Service and Permissions data](policyuniverse/data.json).

_This package can also minify an AWS policy to help you stay under policy size limits. Avoid doing this if possible, as it creates ugly policies._ 💩

# Install:

`pip install policyuniverse`

# Usage:

- [ARN class](#reading-arns)
- [Policy class](#iam-and-resource-policies)
- [Statement class](#statements)
- [Action Categories](#action-categories)
- [Expanding and Minification](#expanding-and-minification)

## Reading ARNs

```python
from policyuniverse.arn import ARN
arn = ARN('arn:aws:iam::012345678910:role/SomeTestRoleForTesting')
assert arn.error == False
assert arn.tech == 'iam'
assert arn.region == ''  # IAM is universal/global
assert arn.account_number == '012345678910'
assert arn.name == 'role/SomeTestRoleForTesting'
assert arn.partition == 'aws'
assert arn.root == False  # Not the root ARN
assert arn.service == False  # Not an AWS service like lambda.amazonaws.com

arn = ARN('012345678910')
assert arn.account_number == '012345678910'

arn = ARN('lambda.amazonaws.com')
assert arn.service == True
assert arn.tech == 'lambda'
```

## IAM and Resource Policies

### Policy with multiple statements
```python
# Two statements, both with conditions
policy05 = dict(
    Version='2010-08-14',
    Statement=[
        dict(
            Effect='Allow',
            Principal='arn:aws:iam::012345678910:root',
            Action=['s3:*'],
            Resource='*',
            Condition={
                'IpAddress': {
                    'AWS:SourceIP': ['0.0.0.0/0']
                }}),
        dict(
            Effect='Allow',
            Principal='arn:aws:iam::*:role/Hello',
            Action=['ec2:*'],
            Resource='*',
            Condition={
                'StringLike': {
                    'AWS:SourceOwner': '012345678910'
                }})
        ])

from policyuniverse.policy import Policy
from policyuniverse.statement import ConditionTuple, PrincipalTuple

policy = Policy(policy05)
assert policy.whos_allowed() == set([
    PrincipalTuple(category='principal', value='arn:aws:iam::*:role/Hello'),
    PrincipalTuple(category='principal', value='arn:aws:iam::012345678910:root'),
    ConditionTuple(category='cidr', value='0.0.0.0/0'),
    ConditionTuple(category='account', value='012345678910')
])

# The given policy is not internet accessible.
# The first statement is limited by the principal, and the condition is basically a no-op.
# The second statement has a wildcard principal, but uses the condition to lock it down.
assert policy.is_internet_accessible() == False
```

### Internet Accessible Policy:

```python
# An internet accessible policy:
policy01 = dict(
    Version='2012-10-08',
    Statement=dict(
        Effect='Allow',
        Principal='*',
        Action=['rds:*'],
        Resource='*',
        Condition={
            'IpAddress': {
                'AWS:SourceIP': ['0.0.0.0/0']
            }
        }))

policy = Policy(policy01)
assert policy.is_internet_accessible() == True
assert policy.internet_accessible_actions() == set(['rds:*'])
```

## Statements

A policy is simply a collection of statements.

```python
statement12 = dict(
    Effect='Allow',
    Principal='*',
    Action=['rds:*'],
    Resource='*',
    Condition={
        'StringEquals': {
            'AWS:SourceVPC': 'vpc-111111',
            'AWS:Sourcevpce': 'vpce-111111',
            'AWS:SourceOwner': '012345678910',
            'AWS:SourceAccount': '012345678910'
        },
        'StringLike': {
            'AWS:userid': 'AROAI1111111111111111:*'
        },
        'ARNLike': {
            'AWS:SourceArn': 'arn:aws:iam::012345678910:role/Admin'
        },
        'IpAddressIfExists': {
            'AWS:SourceIP': [
                '123.45.67.89',
                '10.0.7.0/24',
                '172.16.0.0/16']
        }
    })

from policyuniverse.statement import Statement
from policyuniverse.statement import ConditionTuple, PrincipalTuple

statement = Statement(statement12)
assert statement.effect == 'Allow'
assert statement.actions == set(['rds:*'])

# rds:* expands out to ~88 individual permissions
assert len(statement.actions_expanded) == 88

assert statement.uses_not_principal() == False
assert statement.principals == set(['*'])
assert statement.condition_arns == set(['arn:aws:iam::012345678910:role/Admin'])
assert statement.condition_accounts == set(['012345678910'])
assert statement.condition_userids == set(['AROAI1111111111111111:*'])
assert statement.condition_cidrs == set(['10.0.7.0/24', '172.16.0.0/16', '123.45.67.89'])
assert statement.condition_vpcs == set(['vpc-111111'])
assert statement.condition_vpces == set(['vpce-111111'])
assert statement.is_internet_accessible() == False
assert statement.whos_allowed() == set([
    PrincipalTuple(category='principal', value='*'),
    ConditionTuple(category='cidr', value='123.45.67.89'),
    ConditionTuple(category='account', value='012345678910'),
    ConditionTuple(category='userid', value='AROAI1111111111111111:*'),
    ConditionTuple(category='vpc', value='vpc-111111'),
    ConditionTuple(category='arn', value='arn:aws:iam::012345678910:role/Admin'),
    ConditionTuple(category='cidr', value='172.16.0.0/16'),
    ConditionTuple(category='vpce', value='vpce-111111'),
    ConditionTuple(category='cidr', value='10.0.7.0/24')])

```


## Action Categories
```python
policy = {
        "Statement": [{
            "Action": ["s3:put*", "sqs:get*", "sns:*"],
            "Resource": "*",
            "Effect": "Allow"
          }]
      }

from policyuniverse.policy import Policy
p = Policy(policy)
for k, v in p.action_summary().items():
    print(k,v)
>>> ('s3', set([u'Write', u'Permissions', u'Tagging']))
>>> ('sqs', set([u'List']))
>>> ('sns', set([u'List', u'Read', u'Write', u'Permissions']))
```
Possible categories are `Permissions`, `Write`, `Read`, `Tagging`, and `List`.  This data can be used to summarize statements and policies and to look for sensitive permissions.

## Expanding and Minification
```python
from policyuniverse.expander_minimizer import expand_policy
from policyuniverse.expander_minimizer import minimize_policy

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

