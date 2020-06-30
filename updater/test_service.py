import logging
import unittest
import json
from service import Service

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.url = ""
        self.aws_response = {
            "serviceDisplayName": "Simple Queue Service",
            "serviceName": "sqs",
            "description": "For Queues and Stuffs",
            "arnFormat": "arn:blah:blah:blah",
            "arnRegex": "arn:.+:.+:.+",
            "_links": {"actions": {"href": "/actions"}},
            "actionsDocRoot": "",
            "authZDocPage": "",
            "conceptsDocRoot": "",
            "contextKeysDocRoot": "",
            "apiDetailRoot": "",
            "apiDocRoot": "",
            "apiReferenceDocPage": "",
        }

    def test(self):
        expected = dict(
            prefix="sqs",
            description="For Queues and Stuffs",
            arn_format="arn:blah:blah:blah",
            arn_regex="arn:.+:.+:.+",
            docs=dict(
                actions_doc_root="",
                authz_doc_page="",
                concepts_doc_root="",
                context_keys_doc_root="",
                api_detail_root="",
                api_doc_root="",
                api_reference_doc_page="",
            ),
            actions=dict(),
        )
        expected = json.dumps(expected, sort_keys=True, indent=2)

        my_service = Service(self.url, self.aws_response)
        response = json.dumps(my_service.toJSON(), sort_keys=True, indent=2)
        assert expected == response
