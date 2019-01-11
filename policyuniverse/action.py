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
.. module: policyuniverse.action
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor::  Patrick Kelley <pkelley@netflix.com>

"""

def build_service_actions_from_service_data(service_data):
    permissions = set()
    for service_name in service_data:
        prefix = service_data[service_name]["prefix"]
        service_actions = service_data[service_name]["actions"]
        for action in service_actions:
            permissions.add("{}:{}".format(prefix, action.lower()))
    return permissions

# TODO: Helper Action class
# May also want to create a service.py