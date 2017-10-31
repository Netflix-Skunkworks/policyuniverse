import json
import os
from collections import defaultdict
from policyuniverse import action_categories


def reformat_console_data(filename):
    """
    The AWS Console has a ~3.5MB file mapping actions to 
    groups (and other info).

    URL is:
    https://console.aws.amazon.com/iam/api/policies/arn:aws:iam::aws:policy%C2%B6AdministratorAccess/version/v1/policysummary

    Must be authenticated, and probably also requires CSRF token, so I typically
    just pull the contents from the Network tab of the Chrome inspector.
    
    This method will reformat that into a structure containing only
    the data we care about.
    """
    administrator_access = json.load(open(filename, 'r'))
    groups = defaultdict(list)
    for service in administrator_access['serviceDetails']:
        prefix = service['servicePrefix']
        for action in service['allowedActions']:
            action_name = '{prefix}:{name}'.format(prefix=prefix, name=action['name'])
            category = translate_aws_action_groups(action['actionGroups'])
            groups[action_name.lower()] = category

    with open(filename, 'w') as outfile:
        json.dump(groups, outfile, indent=2, sort_keys=True)

def translate_aws_action_groups(groups):
    """
    Problem - AWS provides the following four groups:
        - Permissiosn
        - ReadWrite
        - ListOnly
        - ReadOnly
    
    The meaning of these groups was not immediately obvious to me.
    
    Permissions: ability to modify (create/update/remove) permissions.
    ReadWrite: Indicates a data-plane operation.
    ReadOnly: Always used with ReadWrite. Indicates a read-only data-plane operation.
    ListOnly: Always used with [ReadWrite, ReadOnly]. Indicates an action which
        lists resources, which is a subcategory of read-only data-plane operations.
    
    So an action with ReadWrite, but without ReadOnly, is a mutating data-plane operation.
    An action with Permission never has any other groups.
    
    This method will take the AWS categories and translate them to one of the following:
    
    - DataPlaneMutating
    - DataPlaneListRead
    - Permissions
    """
    if 'Permissions' in groups:
        return 'Permissions'
    if 'ReadOnly' in groups or 'ListOnly' in groups:
        return 'DataPlaneListRead'
    if 'ReadWrite' in groups:
        return 'DataPlaneMutating'
    return 'Unknown'

def categories_for_actions(actions):
    """
    Given an iterable of actions, return a mapping of action groups.
    
    actions: {'ec2:authorizesecuritygroupingress', 'iam:putrolepolicy', 'iam:listroles'}
    
    Returns:
        {
            'ec2': {'DataPlaneMutating'},
            'iam': {'Permissions', 'DataPlaneListRead'})
        }
    """
    groups = defaultdict(set)
    for action in actions:
        service = action.split(':')[0]
        groups[service].add(action_categories.get(action))
    return groups

def actions_for_category(category):
    """
    Returns set of actions containing each group passed in.
    
    Param:
        category must be in {'Permissions', 'DataPlaneMutating', 'DataPlaneListRead}
    
    Returns:
        set of matching actions
    """
    actions = set()
    for action, action_category in action_categories.items():
        if action_category == category:
           actions.add(action)
    return actions