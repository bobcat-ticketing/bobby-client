"""Test BoB Token API"""

import unittest
import logging
import os
from datetime import datetime, timezone
import dateutil.parser

from bobby_client.env import TestEnvironment
from bobby_client.utils import b64e


class TestTokenAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        self.env = TestEnvironment.create_from_config_file(api='token')
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
            logging.info("Found token with pid=%d serial=%d", params['pid'], params['serial'])

    def test_get_by_unknown_serial(self):
        """Get token by serial"""
        request_uri = '{}/token'.format(self.env.endpoint('token'))
        for params in self.env.config['test']['token'].get('unknown_serials', []):
            response = self.session.get(request_uri, params=params)
            self.assertEqual(response.status_code, 404)

    def test_get_by_id(self):
        """Get token by id"""
        request_uri = '{}/token'.format(self.env.endpoint('token'))
        for token_id in self.env.config['test']['token'].get('known_ids', []):
            response = self.session.get(f"{request_uri}/{token_id}")
            self.assertEqual(response.status_code, 200)
            logging.info("Found token with id=%s", token_id)

    def test_get_unknown_id(self):
        """Get unknown token id"""
        request_uri = '{}/token'.format(self.env.endpoint('token'))
        token_id = b64e(os.urandom(32)).decode()
        response = self.session.get(f"{request_uri}/{token_id}")
        self.assertEqual(response.status_code, 404)

    def test_get_revocation_list(self):
        """Get token revocation list with serial"""
        now = datetime.now(timezone.utc)
        request_uri = '{}/token/revocationlist?revocationListStartEntryId=0'.format(self.env.endpoint('token'))
        response = self.session.get(request_uri)
        self.assertEqual(response.status_code, 200)
        count_effective = 0
        count_expired = 0
        for r in response.json():
            if 'expire' in r:
                expire = dateutil.parser.parse(r['expire'])
                if expire <= now:
                    count_expired += 1
                    continue
            count_effective += 1
        logging.info("Expired entries: %d", count_expired)
        logging.info("Effective entries: %d", count_effective)


if __name__ == '__main__':
    unittest.main()
