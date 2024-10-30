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
.. moduleauthor::  Patrick Kelley <patrickbarrettkelley@gmail.com> @patrickbkelley

"""

def build_service_actions_from_service_data(iam_data):
    permissions = set()
    for service_key in iam_data.services.get_service_keys():
        service_name = iam_data.services.get_service_name(service_key)
        for action in iam_data.actions.get_actions_for_service(service_key):
            permissions.add("{}:{}".format(service_key, action.lower()))
    return permissions


# TODO: Helper Action class
# May also want to create a service.py
