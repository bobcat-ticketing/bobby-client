"""Test BoB Product API"""

import json
import logging
import unittest

from bobby_client.utils import b64d
from bobby_client.env import TestEnvironment


class TestProductAPI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file(api='product')
        self.session = self.env.get_session()
        filename = self.env.config['test']['product'].get('manifests')
        if filename is not None:
            with open(filename) as manifests_file:
                self.manifests = json.load(manifests_file)
        else:
            self.manifests = []
        self.env.authenticate(self.session, api='product')
        self.save_results = self.env.config['global'].get('save_results', False)

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
            test_id = selector.get('id')
            logging.info("Running test %s", test_id)
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

            manifest = result['manifest']

            if self.save_results:
                payload_filename = f"{test_id}.json"
                manifest_filename = f"{test_id}.bin"
                logging.info("Saving payload to %s", payload_filename)
                with open(payload_filename, 'wt') as output_file:
                    json.dump(result, output_file, indent=4)
                logging.info("Saving manifest to %s", manifest_filename)
                with open(manifest_filename, 'wb') as output_file:
                    output_file.write(b64d(manifest.encode()))

            # refetch manifest and compare
            self.assertTrue('Location' in response.headers)
            manifest_location = response.headers['Location']
            logging.info("Manifest location: %s", manifest_location)
            response = self.session.get(manifest_location)
            self.assertEqual(response.status_code, 200)
            result = response.json()
            manifest_refetched = result['manifest']
            self.assertEqual(manifest, manifest_refetched)

    def test_categories(self):
        """Test categories"""

        for category in ['fare', 'product', 'traveller']:
            request_uri = '{}/productcat/{}'.format(self.env.endpoint('product'), category)
            response = self.session.get(request_uri)
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(len(result) > 0)
            logging.info("Found %s category %s", category, result)


if __name__ == '__main__':
    unittest.main()
