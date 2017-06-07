"""Test BoB Authentication API"""

import unittest
import logging
import uuid
from bob_test.env import TestEnvironment


BAD_ENTITY_ID = str(uuid.uuid4())
BAD_CERT = 'badcert.pem'


class TestAuthenticationAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file('examples/config.yaml')

    def tearDown(self):
        self.env.close()

    def test_get_token(self):
        """Get BoB auth token (good)"""
        response = self.env.get_auth_response()
        self.assertEqual(response.status_code, 200)

    def test_bad_entity_id(self):
        """Get BoB auth token with bad entity_id"""
        response = self.env.get_auth_response(entity_id=BAD_ENTITY_ID)
        self.assertEqual(response.status_code, 404)

    def test_bad_certificate(self):
        """Get BoB auth token with bad certificate"""
        response = self.env.get_auth_response(cert=(BAD_CERT,None))
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
