"""Test BoB Product API"""

import unittest
import logging
from bobby_client.env import TestEnvironment


PRODUCT_QUERY = {
    'originLocation': "7411233",
    'destinationLocation': "7422840",
    'fareCategoryId': "day",
    'productCategoryId': "single",
    'travellerCategoryId': "a"
}
PRODUCT_FILTER = {
    'group': {'groupType':'zone', 'groupIds': ['820', '821', '822']},
    'travellerCategoryIds': ['a']
}


class TestProductAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()
        self.session = self.env.get_session()
        self.env.authenticate(self.session, api='product')

    def tearDown(self):
        self.session.close()
        self.env.close()

    def test_product_search(self):
        """Test product search"""

        request_uri = '{}/product'.format(self.env.endpoint('product'))
        response = self.session.post(request_uri, json=PRODUCT_FILTER)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertTrue(len(result) > 0)
        logging.debug(result)

    def test_product_query(self):
        """Test product search using query parameters"""

        request_uri = '{}/product'.format(self.env.endpoint('product'))
        response = self.session.get(request_uri, params=PRODUCT_QUERY)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertTrue(len(result) > 0)
        logging.debug(result)

    def test_manifest(self):
        """Test manifest search"""

        # search product
        request_uri = '{}/product'.format(self.env.endpoint('product'))
        response = self.session.post(request_uri, json=PRODUCT_FILTER)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(len(result) > 0)

        # request manifest for the first product we're offered
        product_id = result[0][0]['productId']
        logging.info("Pick product: %s", product_id)
        manifest_request = {
            'productSelections': [{'productId': product_id}]
        }
        request_uri = '{}/manifest'.format(self.env.endpoint('product'))
        response = self.session.post(request_uri, json=manifest_request)
        self.assertEqual(response.status_code, 201)

        result = response.json()
        self.assertTrue(len(result) > 0)
        logging.debug(result)

        # refetch manifest and compare
        manifest = result['manifest']
        manifest_location = response.headers['Location']
        logging.info("Manifest location: %s", manifest_location)
        response = self.session.get(manifest_location)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        manifest_refetched = result['manifest']
        self.assertEqual(manifest, manifest_refetched)

    def test_product_categories(self):
        """Test product categories"""

        for category in ['fare', 'product', 'traveller']:
            request_uri = '{}/productcat/{}'.format(self.env.endpoint('product'), category)
            response = self.session.get(request_uri)
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(len(result) > 0)
            logging.debug(result)


if __name__ == '__main__':
    unittest.main()
