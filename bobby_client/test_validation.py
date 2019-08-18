"""Test BoB Validation API"""

import unittest
import logging
from bobby_client.env import TestEnvironment


class TestValidationAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file(api='validation')
        self.session = self.env.get_session()
        self.env.authenticate(self.session, api='validation')

    def tearDown(self):
        self.session.close()
        self.env.close()

    def test_get_blacklist(self):
        """Test get blacklist"""
        request_uri = '{}/blacklist?blacklistEntryId=0'.format(self.env.endpoint('validation'))
        response = self.session.get(request_uri)
        self.assertEqual(response.status_code, 200)

    def test_get_all_ticklemacrosets(self):
        """Test get tickle macros"""
        request_uri = '{}/ticklemacros'.format(self.env.endpoint('validation'))
        response = self.session.get(request_uri)
        self.assertEqual(response.status_code, 200)

    def test_get_single_ticklemacroset(self):
        """Test get tickle macros"""
        tickle_macro_serials = self.env.config['test']['validation'].get('tickle_macro_serials', [])
        for serial in tickle_macro_serials:
            request_uri = '{}/ticklemacros/{}'.format(self.env.endpoint('validation'), serial)
            response = self.session.get(request_uri)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 3)
            self.assertIn('macros', data)
            self.assertIn('pid', data)
            self.assertEqual(data['serial'], serial)


if __name__ == '__main__':
    unittest.main()
