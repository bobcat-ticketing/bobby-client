"""Test BoB Token API"""

import unittest
import logging
import os

from bobby_client.env import TestEnvironment
from bobby_client.utils import b64e


class TestTokenAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()
        self.session = self.env.get_session()
        self.env.authenticate(self.session, api='token')

    def tearDown(self):
        self.session.close()
        self.env.close()

    def test_get_by_serial(self):
        """Get token by serial"""
        request_uri = '{}/token'.format(self.env.endpoint('token'))
        for params in self.env.config['test']['token'].get('known_serials', []):
            response = self.session.get(request_uri, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.json()) == 1)
        for params in self.env.config['test']['token'].get('unknown_serials', []):
            response = self.session.get(request_uri, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.json()) == 0)

    def test_get_by_id(self):
        """Get token by id"""
        request_uri = '{}/token'.format(self.env.endpoint('token'))
        for token_id in self.env.config['test']['token'].get('known_ids', []):
            response = self.session.get(f"{request_uri}/{token_id}")
            self.assertEqual(response.status_code, 200)

    def test_get_unknown_id(self):
        """Get unknown token id"""
        request_uri = '{}/token'.format(self.env.endpoint('token'))
        token_id = b64e(os.urandom(32)).decode()
        response = self.session.get(f"{request_uri}/{token_id}")
        self.assertEqual(response.status_code, 404)

    def test_get_revocation_list(self):
        """Get token revocation list with serial"""
        request_uri = '{}/token/revocationlist?revocationListStartEntryId=0'.format(self.env.endpoint('token'))
        response = self.session.get(request_uri)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
