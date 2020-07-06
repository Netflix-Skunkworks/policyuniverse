class ServiceActionConditionKey:
    """Stores a condition key that is associated with a ServiceAction."""

    def __init__(self, body):
        self.doc_page_rel = body["docPageRel"]
        self.name = body["name"]
        self.value_type = body["type"]
        self.description = body["description"]


class ServiceAction:
    """Stores data on an AWS service permission

    Args:
        service (str): A python object representing an AWS service
        body (dict): Contains data about one permission.
    """

    def __init__(self, service, body):
        self.service = service
        self.description = self._get_description(body)
        self.action_groups = self._get_action_groups(body)
        self.api_doc = self._get_api_doc(body)
        self.doc_page_rel = self._get_doc_page_rel(body)
        self.doc_page = self._get_doc_page(body)
        self.action_name = self._get_action_name(body)
        self._condition_keys = self._get_condition_keys(body)

    @property
    def condition_keys(self):
        """Simplify access to condition keys."""
        return sorted([k.name for k in self._condition_keys])

    def calculate_action_groups(self):
        """Convert AWS Action groups into something that makes more sense."""
        if "Permissions" in self.action_groups:
            return "Permissions"
        if "ListOnly" in self.action_groups:
            return "List"
        if "ReadOnly" in self.action_groups:
            return "Read"
        if "Tagging" in self.action_groups:
            return "Tagging"
        if "ReadWrite" in self.action_groups:
            return "Write"
        return "Unknown"

    def toJSON(self):
        """Actually returns a dict."""
        return dict(
            description=self.description,
            aws_action_groups=self.action_groups,
            calculated_action_group=self.calculate_action_groups(),
            docs=dict(
                api_doc=self.api_doc,
                doc_page_rel=self.doc_page_rel,
                doc_page=self.doc_page,
            ),
            condition_keys=self.condition_keys,
        )

    def _get_description(self, body):
        return body["description"]

    def _get_action_groups(self, body):
        return body["actionGroups"]

    def _get_api_doc(self, body):
        return body["apiDoc"]

    def _get_doc_page_rel(self, body):
        return body["docPageRel"]

    def _get_doc_page(self, body):
        return body["docPage"]

    def _get_action_name(self, body):
        return body["id"]

    def _get_condition_keys(self, body):
        keys = list()
        for key_body in body["contextKeys"]:
            key = ServiceActionConditionKey(key_body)
            keys.append(key)
        return keys
