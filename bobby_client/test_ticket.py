"""Test BoB Ticket API"""

import unittest


class TestTicketAPI(unittest.TestCase):

    def setUp(self):
        #logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()

    def tearDown(self):
        self.env.close()


if __name__ == '__main__':
    unittest.main()
