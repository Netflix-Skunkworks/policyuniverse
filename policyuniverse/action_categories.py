from collections import defaultdict

from policyuniverse import _action_categories

def translate_aws_action_groups(groups):
    """
    Problem - AWS provides the following five groups:
        - Permissions
        - ReadWrite
        - ListOnly
        - ReadOnly
        - Tagging

    The meaning of these groups was not immediately obvious to me.

    Permissions: ability to modify (create/update/remove) permissions.
    ReadWrite: Indicates a data-plane operation.
    ReadOnly: Always used with ReadWrite. Indicates a read-only data-plane operation.
    ListOnly: Always used with [ReadWrite, ReadOnly]. Indicates an action which
        lists resources, which is a subcategory of read-only data-plane operations.
    Tagging: Always used with ReadWrite. Indicates a permission that can mutate tags.

    So an action with ReadWrite, but without ReadOnly, is a mutating data-plane operation.
    An action with Permission never has any other groups.

    This method will take the AWS categories and translate them to one of the following:

    - List
    - Read
    - Tagging
    - ReadWrite
    - Permissions
    """
    if "Permissions" in groups:
        return "Permissions"
    if "ListOnly" in groups or "List" in groups:
        return "List"
    if "Read" in groups or "ReadOnly" in groups:
        return "Read"
    if "Tagging" in groups:
        return "Tagging"
    if "Write" in groups or "ReadWrite" in groups:
        return "Write"
    return "Unknown"


def build_action_categories_from_service_data(iam_data):
    action_categories = dict()
    for service_key in iam_data.services.get_service_keys():
        service_name = iam_data.services.get_service_name(service_key)
        for action in iam_data.actions.get_actions_for_service(service_key):
            key = "{}:{}".format(service_key, action.lower())
            action_details = iam_data.actions.get_action_details(service_key, action)
            action_categories[key] = translate_aws_action_groups(action_details['accessLevel'])
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
        service = action.split(":")[0]
        groups[service].add(_action_categories.get(action))
    return groups


def actions_for_category(category):
    """
    Returns set of actions containing each group passed in.

    Param:
        category must be in {'Permissions', 'List', 'Read', 'Tagging', 'Write'}

    Returns:
        set of matching actions
    """
    actions = set()
    for action, action_category in _action_categories.items():
        if action_category == category:
            actions.add(action)
    return actions
