import json
import os
import sys
import logging

_action_categories = dict()
all_permissions = set()
from policyuniverse.action_categories import build_action_categories_from_service_data
from policyuniverse.action import build_service_actions_from_service_data


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read Input Data
service_data_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data.json')

service_data = json.load(open(service_data_path, 'r'))

_action_categories.update(build_action_categories_from_service_data(service_data))
all_permissions.update(build_service_actions_from_service_data(service_data))

# These have been refactored to other files, but
# some dependencies still try to import them from here:
from policyuniverse.expander_minimizer import expand_policy
from policyuniverse.expander_minimizer import get_actions_from_statement
