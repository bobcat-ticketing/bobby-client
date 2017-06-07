"""Test BoB Validation API"""

import unittest
import logging
import json
from bob_test.env import TestEnvironment


class TestValidationAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file('examples/config.yaml')
        self.session = self.env.get_session()
        self.env.authenticate(self.session)

    def tearDown(self):
        self.session.close()
        self.env.close()

    def test_get_blacklist(self):
        """Test get blacklist"""
        request_uri = '{}/blacklist?blacklistEntryId=0'.format(self.env.endpoint('device'))
        response = self.session.get(request_uri)
        self.assertEqual(response.status_code, 200)
        logging.debug(response.json())
        response.close()

    def test_get_ticklemacros(self):
        """Test get tickle macros"""    

        request_uri = '{}/ticklemacros'.format(self.env.endpoint('validation'))
        response = self.session.get(request_uri)
        self.assertEqual(response.status_code, 200)

        tickle_macro_serials = self.env.config['test']['validation'].get('tickle_macro_serials', [])
        for serial in tickle_macro_serials:
            request_uri = '{}/ticklemacros?serial={}'.format(self.env.endpoint('validation'), serial)
            response = self.session.get(request_uri)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            logging.debug(data)
            response.close()
            self.assertEqual(len(data), 1)


if __name__ == '__main__':
    unittest.main()
