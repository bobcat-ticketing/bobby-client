"""Test BoB Product API: Filters"""

import unittest
import logging
import json
from bobby_client.env import TestEnvironment


class TestProductAPIwithFilters(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()
        self.session = self.env.get_session()
        filename = self.env.config['test']['product']['filters']
        with open(filename) as filters_file:
            self.filters = json.load(filters_file)
        self.env.authenticate(self.session, api='product')

    def tearDown(self):
        self.session.close()
        self.env.close()

    def _base_test_product(self, filter_type: str):
        """Test product filter using payload or query parameters"""

        for test_case in self.filters[filter_type]:
            request_uri = '{}/product'.format(self.env.endpoint('product'))

            if test_case['operation'] == 'get':
                logging.info("GET: %s", request_uri)
                response = self.session.get(request_uri,
                                            params=test_case.get('query'))
            elif test_case['operation'] == 'post':
                logging.info("POST: %s", request_uri)
                response = self.session.post(request_uri,
                                             params=test_case.get('query'),
                                             json=test_case.get('payload'))
            else:
                raise RuntimeError('Unknown operation: ' + test_case['operation'])

            self.assertEqual(response.status_code, test_case['code'])

            if response.status_code == 200:
                result = response.json()

                if 'amount' in test_case:
                    unexpected = []
                    for prodset in result:
                        for prod in prodset:
                            prod_amount = prod['fares'][0]['amount']
                            found = None
                            for expect_amount in test_case['amount']:
                                if expect_amount - 0.01 < prod_amount < expect_amount + 0.01:
                                    found = expect_amount
                            if found:
                                test_case['amount'].remove(found)
                            else:
                                unexpected.append(prod_amount)
                    self.assertEqual(unexpected, test_case['amount'])

    def test_product_group_filters(self):
        """Test product group filters"""
        self._base_test_product("group")

    def test_product_query_filters(self):
        """Test product query filters"""
        self._base_test_product("query")

    def test_product_route_filters(self):
        """Test product route filters"""
        self._base_test_product("route")


if __name__ == '__main__':
    unittest.main()
