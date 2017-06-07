"""Test BoB Production API"""

import unittest


class TestProductAPI(unittest.TestCase):

    def setUp(self):
        #logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file('examples/config.yaml')

    def tearDown(self):
        self.env.close()


if __name__ == '__main__':
    unittest.main()
