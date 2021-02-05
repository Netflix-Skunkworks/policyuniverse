#     Copyright 2018 Netflix, Inc.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
"""
.. module: policyuniverse.expander_minimizer
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Patrick Kelley <<patrickbarrettkelley@gmail.com> @patrickbkelley

"""
from __future__ import print_function
from policyuniverse import all_permissions
from policyuniverse.common import ensure_array
import json
import fnmatch
import sys
import copy

policy_headers = ["rolepolicies", "grouppolicies", "userpolicies", "policy"]


def expand_minimize_over_policies(policies, activity, **kwargs):
    for header in policy_headers:
        if header in policies:
            output = {header: {}}
            for policy in policies[header]:
                output[header][policy] = activity(
                    policy=policies[header][policy], **kwargs
                )
            return output

    return activity(policy=policies, **kwargs)


def _get_prefixes_for_action(action):
    """
    :param action: iam:cat
    :return: [ "iam:", "iam:c", "iam:ca", "iam:cat" ]
    """
    (technology, permission) = action.split(":")
    retval = ["{}:".format(technology)]
    phrase = ""
    for char in permission:
        newphrase = "{}{}".format(phrase, char)
        retval.append("{}:{}".format(technology, newphrase))
        phrase = newphrase
    return retval


def _expand(action):
    """
    :param action: 'autoscaling:*'
    :return: A list of all autoscaling permissions matching the wildcard
    """
    expanded = fnmatch.filter(all_permissions, action.lower())
    # if we get a wildcard for a tech we've never heard of, just return the wildcard
    if not expanded:
        return [action]
    return expanded


def _expand_wildcard_action(actions):
    """Expand wildcards in a list of actions (or a single action string), returning a list of all matching actions.

    :param actions: ['autoscaling:*']
    :return: A list of all permissions matching the action globs
    """
    if isinstance(actions, str):
        # Bail early if we have a string with no wildcard
        if "*" not in actions:
            return [actions.lower()]
        actions = [actions]

    # Map _expand function to action list, resulting in a list of lists of expanded actions.
    temp = map(_expand, actions)

    # This flattens the list of lists. It's hard to read, but it's a hot path and the optimization
    # speeds it up by 90% or more.
    expanded = [item.lower() for sublist in temp for item in sublist]

    return expanded


def _get_desired_actions_from_statement(statement):
    desired_actions = set()
    actions = _expand_wildcard_action(statement["Action"])

    for action in actions:
        if action not in all_permissions:
            raise Exception(
                "Desired action not found in master permission list. {}".format(action)
            )
        desired_actions.add(action)

    return desired_actions


def _get_denied_prefixes_from_desired(desired_actions):
    denied_actions = all_permissions.difference(desired_actions)
    denied_prefixes = set()
    for denied_action in denied_actions:
        for denied_prefix in _get_prefixes_for_action(denied_action):
            denied_prefixes.add(denied_prefix)

    return denied_prefixes


def _check_min_permission_length(permission, minchars=None):
    if minchars and len(permission) < int(minchars) and permission != "":
        print(
            "Skipping prefix {} because length of {}".format(
                permission, len(permission)
            ),
            file=sys.stderr,
        )
        return True
    return False


def minimize_statement_actions(statement, minchars=None):
    minimized_actions = set()

    if statement["Effect"] != "Allow":
        raise Exception("Minification does not currently work on Deny statements.")

    desired_actions = _get_desired_actions_from_statement(statement)
    denied_prefixes = _get_denied_prefixes_from_desired(desired_actions)

    for action in desired_actions:
        if action in denied_prefixes:
            print("Action is a denied prefix. Action: {}".format(action))
            minimized_actions.add(action)
            continue

        found_prefix = False
        prefixes = _get_prefixes_for_action(action)
        for prefix in prefixes:

            permission = prefix.split(":")[1]
            if _check_min_permission_length(permission, minchars=minchars):
                continue

            if prefix not in denied_prefixes:
                if prefix not in desired_actions:
                    prefix = "{}*".format(prefix)
                minimized_actions.add(prefix)
                found_prefix = True
                break

        if not found_prefix:
            print("Could not suitable prefix. Defaulting to {}".format(prefixes[-1]))
            minimized_actions.add(prefixes[-1])

    # sort the actions
    minimized_actions_list = list(minimized_actions)
    minimized_actions_list.sort()

    return minimized_actions_list


def get_actions_from_statement(statement):
    allowed_actions = set()
    actions = ensure_array(statement.get("Action", []))

    for action in actions:
        allowed_actions = allowed_actions.union(set(_expand_wildcard_action(action)))

    inverted_actions = set()
    not_actions = ensure_array(statement.get("NotAction", []))

    for action in not_actions:
        inverted_actions = inverted_actions.union(set(_expand_wildcard_action(action)))

    if inverted_actions:
        actions = _invert_actions(inverted_actions)
        allowed_actions = allowed_actions.union(actions)

    return allowed_actions


def _invert_actions(actions):
    from policyuniverse import all_permissions

    return all_permissions.difference(actions)


def expand_policy(policy=None, expand_deny=False):
    # Perform a deepcopy to avoid mutating the input
    result = copy.deepcopy(policy)

    result["Statement"] = ensure_array(result["Statement"])
    for statement in result["Statement"]:
        if statement["Effect"].lower() == "deny" and not expand_deny:
            continue
        actions = get_actions_from_statement(statement)
        if "NotAction" in statement:
            del statement["NotAction"]
        statement["Action"] = sorted(list(actions))

    return result


def minimize_policy(policy=None, minchars=None):

    str_pol = json.dumps(policy, indent=2)
    size = len(str_pol)

    for statement in policy["Statement"]:
        minimized_actions = minimize_statement_actions(statement, minchars=minchars)
        statement["Action"] = minimized_actions

    str_end_pol = json.dumps(policy, indent=2)
    end_size = len(str_end_pol)

    # print str_end_pol
    print("Start size: {}. End size: {}".format(size, end_size), file=sys.stderr)
    return policy
