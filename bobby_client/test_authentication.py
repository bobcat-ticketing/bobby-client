"""Test BoB Authentication API"""

import unittest
import logging
import uuid
import json
import time
from jwkest import b64d
from bobby_client.env import TestEnvironment


BAD_ENTITY_ID = str(uuid.uuid4())
BAD_CERT = 'badcert.pem'
TOKEN_ALGS = ('ES256', 'RS256')
TIMESKEW = 300

class TestAuthenticationAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()

    def tearDown(self):
        self.env.close()

    def test_get_token(self):
        """Get BoB auth token (good)"""
        response = self.env.get_auth_response(api='authentication')
        now = int(time.time())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        (header, payload, signature) = data['jwtCompact'].split('.')
        header_dict = json.loads(b64d(header.encode()))
        payload_dict = json.loads(b64d(payload.encode()))
        signature_dict = b64d(signature.encode())

        # check for supported algorithms
        self.assertIn(header_dict['alg'], TOKEN_ALGS)

        # ensure some headers are not missing
        self.assertIsNotNone(header_dict.get('kid'))
        self.assertIsNotNone(payload_dict.get('iss'))
        self.assertIsNotNone(payload_dict.get('sub'))
        self.assertIsNotNone(payload_dict.get('bobAuthZ'))
        self.assertIsNotNone(payload_dict.get('exp'))

        # ensure iat/nbf/exp are reasonable (if provided)
        if 'iat' in payload_dict:
            self.assertTrue(now + TIMESKEW >= payload_dict['iat'])
        if 'nbf' in payload_dict:
            self.assertTrue(now + TIMESKEW >= payload_dict['nbf'])
        if 'exp' in payload_dict:
            self.assertTrue(now - TIMESKEW < payload_dict['exp'])

    def test_bad_entity_id(self):
        """Get BoB auth token with bad entity_id"""
        response = self.env.get_auth_response(entity_id=BAD_ENTITY_ID)
        self.assertEqual(response.status_code, 404)

    def test_no_certificate(self):
        """Get BoB auth token without a certificate"""
        response = self.env.get_auth_response(api='authentication', cert=(None,None))
        self.assertEqual(response.status_code, 401)

    def test_bad_certificate(self):
        """Get BoB auth token with bad certificate"""
        response = self.env.get_auth_response(api='authentication', cert=(BAD_CERT,None))
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
