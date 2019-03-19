import json
import os
from collections import defaultdict
from policyuniverse import _action_categories


def translate_aws_action_groups(groups):
    """
    Problem - AWS provides the following four groups:
        - Permissions
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

    - List
    - Read
    - ReadWrite
    - Permissions
    """
    if 'Permissions' in groups:
        return 'Permissions'
    if 'ListOnly' in groups:
        return 'List'
    if 'ReadOnly' in groups:
        return 'Read'
    if 'ReadWrite' in groups:
        return 'Write'
    return 'Unknown'


def build_action_categories_from_service_data(service_data):
    action_categories = dict()
    for service_name in service_data:
        service_body = service_data[service_name]
        prefix = service_body['prefix']
        service_actions = service_body['actions']
        for service_action, service_action_body in service_actions.items():
            key = '{}:{}'.format(prefix, service_action.lower())
            action_categories[key]=service_action_body['calculated_action_group']
    return action_categories


def categories_for_actions(actions):
    """
    Given an iterable of actions, return a mapping of action groups.
    
    actions: {'ec2:authorizesecuritygroupingress', 'iam:putrolepolicy', 'iam:listroles'}
    
    Returns:
        {
            'ec2': {'Write'},
            'iam': {'Permissions', 'List'})
        }
    """
    groups = defaultdict(set)
    for action in actions:
        service = action.split(':')[0]
        groups[service].add(_action_categories.get(action))
    return groups

def actions_for_category(category):
    """
    Returns set of actions containing each group passed in.
    
    Param:
        category must be in {'Permissions', 'List', 'Read', 'Write'}
    
    Returns:
        set of matching actions
    """
    actions = set()
    for action, action_category in _action_categories.items():
        if action_category == category:
           actions.add(action)
    return actions
