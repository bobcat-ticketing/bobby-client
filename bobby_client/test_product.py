"""Test BoB Product API"""

import unittest
import logging
import json
from bobby_client.env import TestEnvironment


class TestProductAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()
        self.session = self.env.get_session()
        filename = self.env.config['test']['product']['manifests']
        with open(filename) as manifests_file:
            self.manifests = json.load(manifests_file)
        self.env.authenticate(self.session, api='product')

    def tearDown(self):
        self.session.close()
        self.env.close()

    def _find_first_product(self, filter: dict) -> str:
        "Find first product given filter"
        request_uri = '{}/product'.format(self.env.endpoint('product'))
        response = self.session.post(request_uri, json=filter)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(len(result) > 0)
        product_id = result[0][0]['productId']
        logging.info("Picked product: %s", product_id)
        return product_id

    def test_manifest(self):
        """Test manifest search"""

        for selector in self.manifests:
            logging.info("Running test %s", selector.get('id'))
            if 'filter' in selector:
                logging.info("Get manifest via product filter")
                product_id = self._find_first_product(selector['filter'])
                product_selections = [{'productId': product_id}]
            elif 'selection' in selector:
                logging.info("Get manifest via product selection")
                product_selections = selector['selection']
            else:
                raise RuntimeError("Unknown manifest format: " + selector)

            manifest_request = {
                'productSelections': product_selections
            }
            logging.info("Requesting product using: %s", manifest_request)
            request_uri = '{}/manifest'.format(self.env.endpoint('product'))
            response = self.session.post(request_uri, json=manifest_request)
            self.assertEqual(response.status_code, 201)

            result = response.json()
            self.assertTrue(len(result) > 0)

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


if __name__ == '__main__':
    unittest.main()
