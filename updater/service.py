from collections import defaultdict


class Service:
    """Stores data on an AWS service

    Args:
        url (str): The URL where this service is described.
        body (dict): Contains data about service and permissions.
    """

    def __init__(self, url, body):
        self.display_name = self._read_display_name(body)
        self.service_name = self._read_service_name(body)
        self.description = self._read_description(body)
        self.arn_format = self._read_arn_format(body)
        self.arn_regex = self._read_arn_regex(body)

        self.actions_url = self._read_actions_url(body)
        self.service_url = url

        self.actions_doc_root = self._read_actions_doc_root(body)
        self.authz_doc_page = self._read_authz_doc_page(body)
        self.concepts_doc_root = self._read_concepts_doc_root(body)
        self.context_keys_doc_root = self._read_context_keys_doc_root(body)
        self.api_detail_root = self._read_api_detail_root(body)
        self.api_doc_root = self._read_api_doc_root(body)
        self.api_reference_doc_page = self._read_api_reference_doc_page(body)

        self.actions = defaultdict()

    def toJSON(self):
        actions_dict = dict()
        for action_name, action in self.actions.items():
            actions_dict[action_name] = action.toJSON()

        me = dict(
            prefix=self.service_name,
            description=self.description,
            arn_format=self.arn_format,
            arn_regex=self.arn_regex,
            docs=dict(
                actions_doc_root=self.actions_doc_root,
                authz_doc_page=self.authz_doc_page,
                concepts_doc_root=self.concepts_doc_root,
                context_keys_doc_root=self.context_keys_doc_root,
                api_detail_root=self.api_detail_root,
                api_doc_root=self.api_doc_root,
                api_reference_doc_page=self.api_reference_doc_page,
            ),
            actions=actions_dict,
        )

        return me

    def _read_display_name(self, body):
        return body["serviceDisplayName"]

    def _read_service_name(self, body):
        return body["serviceName"]

    def _read_description(self, body):
        return body["description"]

    def _read_arn_format(self, body):
        return body["arnFormat"]

    def _read_arn_regex(self, body):
        return body["arnRegex"]

    def _read_actions_url(self, body):
        return body["_links"]["actions"]["href"]

    def _read_actions_doc_root(self, body):
        return body["actionsDocRoot"]

    def _read_authz_doc_page(self, body):
        return body["authZDocPage"]

    def _read_concepts_doc_root(self, body):
        return body["conceptsDocRoot"]

    def _read_context_keys_doc_root(self, body):
        return body["contextKeysDocRoot"]

    def _read_api_detail_root(self, body):
        return body["apiDetailRoot"]

    def _read_api_doc_root(self, body):
        return body["apiDocRoot"]

    def _read_api_reference_doc_page(self, body):
        return body["apiReferenceDocPage"]
