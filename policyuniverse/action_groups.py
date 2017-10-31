import json
import os
from collections import defaultdict
from policyuniverse import action_groups


def reformat_console_data(filename):
    """
    The AWS Console has a ~3.5MB file mapping actions to 
    groups (and other info).

    URL is:
    https://console.aws.amazon.com/iam/api/policies/arn:aws:iam::aws:policy%C2%B6AdministratorAccess/version/v1/policysummary

    This method will reformat that into a structure containing only
    the data we care about.
    """
    administrator_access = json.load(open(filename, 'r'))
    groups = defaultdict(list)
    for service in administrator_access['serviceDetails']:
        prefix = service['servicePrefix']
        for action in service['allowedActions']:
            action_name = '{prefix}:{name}'.format(prefix=prefix, name=action['name'])
            groups[action_name.lower()].extend(action['actionGroups'])

    with open(filename, 'w') as outfile:
        json.dump(groups, outfile, indent=2, sort_keys=True)

def groups_for_actions(actions):
    """
    Given an iterable of actions, return a mapping of action groups.
    
    actions: {'ec2:authorizesecuritygroupingress', 'iam:putrolepolicy', 'iam:listroles'}
    
    Returns:
        {
            'ec2': {'ReadWrite'},
            'iam': {'Permissions', 'ListOnly', 'ReadOnly', 'ReadWrite'})
        }
    """
    groups = defaultdict(set)
    for action in actions:
        service = action.split(':')[0]
        groups[service] = groups[service].union(set(action_groups.get(action, set())))
    return groups
