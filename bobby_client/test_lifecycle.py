"""Test BoB Lifecycle API"""

import unittest
import logging
from datetime import datetime, timezone
from bobby_client.env import TestEnvironment


PRODUCT_FILTER = {
    'group': {'groupType':'zone', 'groupIds': ['820', '821', '822']},
    'travellerCategoryIds': ['a']
}


class TestTicketLifecycle(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()
        self.session_pos = self.env.get_session()
        self.session_val = self.env.get_session()
        self.env.authenticate(self.session_pos, api='product')
        self.env.authenticate(self.session_val, api='validation')

    def tearDown(self):
        self.session_pos.close()
        self.session_val.close()
        self.env.close()

    def test_sales(self):
        """Test manifest search"""

        # search product
        request_uri = '{}/product'.format(self.env.endpoint('product'))
        response = self.session_pos.post(request_uri, json=PRODUCT_FILTER)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(len(result) > 0)

        # request manifest for the first product we're offered
        product_id = result[0][0]['productId']
        logging.info("Pick product: %s", product_id)
        manifest_request = {
            'productSelections': [{'productId': product_id}]
        }
        request_uri = '{}/manifest'.format(self.env.endpoint('product'))
        response = self.session_pos.post(request_uri, json=manifest_request)
        self.assertEqual(response.status_code, 201)
        result = response.json()
        manifest = result['manifest']

        # issue ticket
        ticket_request = {
            "manifestMtbTemplate": manifest,
            'issueMtb': True
        }
        request_uri = '{}/ticket'.format(self.env.endpoint('ticket'))
        response = self.session_pos.post(request_uri, json=ticket_request)
        self.assertEqual(response.status_code, 201)
        result = response.json()
        ticket_id = result['ticketIds'][0]
        logging.info("TICKET ID: %s", ticket_id)

        # show MTB
        mtb_data = result['ticketBundle']['mtb']
        logging.info("MTB: %s", mtb_data)

        # submit validation event
        request_uri = '{}/validation/{}'.format(self.env.endpoint('validation'),
                                                ticket_id)
        validation_event = {
            "eventType": "validation",
            "time": datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "ticketId": ticket_id
        }
        response = self.session_val.post(request_uri, json=validation_event)
        self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
