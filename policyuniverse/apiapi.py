"""
    Usage:
        apiapi.py (all|mutating) [--csv=output_file]
        apiapi.py score <permission>
"""

import csv
from policyuniverse import global_permissions
import re
from tabulate import tabulate


TAGS = {
    'DATA_PLANE': ['object', 'message', 'publish'],
    'CONTROL_PLANE': ['policy', 'attribute', 'permission'],
    'MUTATING': ['create', 'delete', 'modify', 'add', 'remove', 'set', 'update', 'put'],
    'READ': ['get', 'view', 'list', 'describe'],
    'SIDE_EFFECT': ['send', 'publish', 'start', 'stop', 'export', 'request', 'resend', 'cancel', 'continue', 'estimate', 'execute', 'preview']
}

permissions = dict()
for service_name, service_description in global_permissions.items():
    service = service_description['StringPrefix']
    permissions[service] = dict()
    for action in service_description['Actions']:

        action_words = re.findall('[A-Z][^A-Z]*', action)
        action_words = [word.lower() for word in action_words]
        permissions[service.lower()][action.lower()] = set()

        for tag_name, matches in TAGS.items():
            for match in matches:
                try:
                    for action_word in action_words:
                        if match in action_word:
                            permissions[service.lower()][action.lower()].add(tag_name)
                except IndexError:
                    if action.lower().startswith(match):
                        permissions[service.lower()][action.lower()].add(tag_name)

headers = ['service', 'permission']
headers.extend(TAGS.keys())


def create_permissions_table():
    rows = []
    for service, actions in permissions.items():
        for action, tags in actions.items():
            row = [service, action]

            for tag in TAGS.keys():
                row.append(tag in tags)

            rows.append(row)
    return rows


def create_mutating_table():
    """ Filters permissions by MUTATING or SIDE_EFFECT tag. """
    rows = []
    for service, actions in permissions.items():
        for action, tags in actions.items():
            row = [service, action]

            for tag in TAGS.keys():
                row.append(tag in tags)

            # CONTROL_PLANE && (MUTATING or SIDE_EFFECT)
            # if 'CONTROL_PLANE' in tags:
            if 'MUTATING' in tags:
                rows.append(row)
            if 'SIDE_EFFECT' in tags:
                rows.append(row)
    return rows


def output_csv(filename, rows):
    with open(filename, 'wb') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(headers)
            for row in rows:
                csv_writer.writerow(row)

def score_permission(permission, include_tags=True):
    """
    Returns a risk score for the provided permission.
    
    TODO: Do we need to worry about case?
    LOW to HIGH RISK:
    READ                  1
    READ DATA_PLANE       1+1 = 2
    READ CONTROL_PLANE    1+2 = 3

    SIDE_EFFECT           4

    MUTATING                  5
    MUTATING DATA_PLANE       5+1 = 6
    MUTATING CONTROL_PLANE    5+2 = 7
    * Note: May come back with unusual tag combos until we have this perfected.
    
    :param permission: Permission to score. Like 'ec2:DescribeInstances'
    :param include_tags: When True, will return a set containing all tags associated with the permission [Default: True]
    :return score: Format TBD
    """
    service = permission.split(':')[0].lower()
    action = permission.split(':')[1].lower()
    if service not in permissions.keys() or action not in permissions[service].keys():
        if include_tags:
            return None, None
        return None
    
    tags = permissions[service][action]
    SCORES = { 
        'READ': 1,
        'DATA_PLANE': 1,
        'CONTROL_PLANE': 2,
        'SIDE_EFFECT': 4,
        'MUTATING': 5
    }

    score = 0
    for tag in SCORES:
        if tag in tags:
            score += SCORES[tag]

    if include_tags:
        return score, tags
    else:
        return score


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__, version="APIAPI 1.0")
    if args.get('mutating'):
        rows = create_mutating_table()
    elif args.get('all'):
        rows = create_permissions_table()
    elif args.get('score'):
        score, tags = score_permission(args.get('<permission>'))
        print('Score: {}'.format(score))
        print('Tags: {}'.format(tags))
        exit()

    filename = args.get('--csv')

    if filename:
        output_csv(filename, rows)
    else:
        print tabulate(rows, headers=headers)

