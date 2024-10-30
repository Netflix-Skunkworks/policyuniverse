"""
isort:skip_file
"""
import json
import os
import logging
from iamdata import IAMData

_action_categories = dict()
all_permissions = set()
# autopep8: off
from policyuniverse.action_categories import build_action_categories_from_service_data
from policyuniverse.action import build_service_actions_from_service_data


# Logging
logger = logging.getLogger(__name__)

iam_data = IAMData()
_action_categories.update(build_action_categories_from_service_data(iam_data))
all_permissions.update(build_service_actions_from_service_data(iam_data))

# These have been refactored to other files, but
# some dependencies still try to import them from here:
from policyuniverse.expander_minimizer import expand_policy
from policyuniverse.expander_minimizer import get_actions_from_statement

# autopep8: on
