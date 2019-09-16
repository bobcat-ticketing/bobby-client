"""Test BoB Inspection API"""

import logging
import unittest

from bobby_client.env import TestEnvironment


class TestInspectionAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file(api='inspection')

    def tearDown(self):
        self.env.close()


if __name__ == '__main__':
    unittest.main()
