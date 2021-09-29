#     Copyright 2021 Amazon.com, Inc.
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
.. module: policyuniverse.organization
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor:: Chris Partridge <chris@partridge.tech> @_tweedge

"""
from policyuniverse import logger


class Organization(object):
    organization = None
    root = None
    ou_path = []
    valid_for_child_ous = False
    valid_for_parent_ou = False
    valid_for_all_ous = True
    error = False

    def __init__(self, input):
        components_list = input.split("/")

        for component_index in range(0, len(components_list)):
            component = components_list[component_index]

            if component_index == 0:
                self._parse_organization(component)
            elif component_index == 1:
                self._parse_root(component)
            else:
                self._parse_ou_path(component)

            if self.error:
                return

    def _parse_organization(self, orgid):
        if orgid.startswith("o-") or orgid == "*":
            self.organization = orgid
        else:
            self.error = True
            logger.debug("Organization Org ID parse error [{}].".format(input))

    def _parse_root(self, root):
        if root.startswith("r-") or root == "*":
            self.root = root
        else:
            self.error = True
            logger.debug("Organization root parse error [{}].".format(input))

    def _parse_ou_path(self, ou):
        if self.valid_for_parent_ou or self.valid_for_child_ous:
            self.error = True
            logger.debug("Organization OU validity error [{}].".format(input))
            return

        if not ou:
            self.valid_for_parent_ou = True
        elif ou == "*":
            self.valid_for_child_ous = True
            self.valid_for_parent_ou = True
        elif ou == "ou-*":
            self.valid_for_child_ous = True
        else:
            self.valid_for_all_ous = False

            if ou.startswith("ou-"):
                self.ou_path.append(ou)
            else:
                self.error = True
                logger.debug("Organization OU parse error [{}].".format(input))
