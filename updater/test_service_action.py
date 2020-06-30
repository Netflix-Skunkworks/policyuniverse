import logging
import json
from service import Service
from service_action import ServiceAction
from test_service import ServiceTest

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ServiceActionTest(ServiceTest):
    def setUp(self):
        super(ServiceActionTest, self).setUp()
        self.body = dict(
            description="Remove all entries from Queue",
            actionGroups=["ReadWrite"],
            apiDoc="",
            docPageRel="",
            docPage="",
            id="PurgeQueue",
            contextKeys=list(
                [{'description': 'Filters actions based on the Amazon Id in the request',
                    'docPage': '',
                    'docPageRel': 'https://docs.aws.amazon.com/a4b/latest/APIReference/API_RegisterAVSDevice.html',
                    'name': 'a4b:amazonId',
                    'type': 'String'}]
            ),
        )

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
            actions=dict(
                PurgeQueue=dict(
                    description="Remove all entries from Queue",
                    aws_action_groups=["ReadWrite"],
                    calculated_action_group="Write",
                    condition_keys=["a4b:amazonId"],
                    docs=dict(api_doc="", doc_page_rel="", doc_page=""),
                )
            ),
        )
        expected = json.dumps(expected, sort_keys=True, indent=2)

        # Create Service and Service Action
        my_service = Service(self.url, self.aws_response)
        my_service_action = ServiceAction(my_service, self.body)

        # Associate the two
        my_service.actions[my_service_action.action_name] = my_service_action

        response = json.dumps(my_service.toJSON(), sort_keys=True, indent=2)
        assert expected == response
