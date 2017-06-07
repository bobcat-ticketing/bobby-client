"""Test BoB Device API"""

import unittest
import logging
import json
import uuid
import requests
from jwkest import b64e
from bob_test.env import TestEnvironment


class TestDeviceAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file('examples/config.yaml')
        self.did = b64e(str(uuid.uuid4()).encode()).decode()
        self.session = self.env.get_session()
        self.env.authenticate(self.session)

    def tearDown(self):
        self.session.close()
        self.env.close()

    def test_get_kdk(self):
        """Get KDK"""
        request_uri = "{}/device/kdk".format(self.env.endpoint('device'))
        response = self.session.get(request_uri)
        self.assertEqual(response.status_code, 200)
        logging.debug(response.json())
        response.close()

    def test_get_device_key(self):
        """Get device key"""
        request_uri = "{}/device/key".format(self.env.endpoint('device'))
        payload = {'did': self.did}
        response = self.session.post(request_uri, json=payload)
        self.assertEqual(response.status_code, 201)
        logging.debug(response.json())
        response.close()

    def test_get_bad_kdk(self):
        """Get KDK (unauthenticated)"""
        unauth_session = self.env.get_session()
        request_uri = "{}/device/kdk".format(self.env.endpoint('device'))
        response = unauth_session.get(request_uri)
        self.assertEqual(response.status_code, 401)
        logging.debug(response.json())
        response.close()

    def test_get_bad_device_key(self):
        """Get device key (unauthenticated)"""
        unauth_session = self.env.get_session()
        request_uri = "{}/device/key".format(self.env.endpoint('device'))
        payload = {'did': self.did}
        response = unauth_session.post(request_uri, json=payload)
        self.assertEqual(response.status_code, 401)
        logging.debug(response.json())
        response.close()


if __name__ == '__main__':
    unittest.main()
