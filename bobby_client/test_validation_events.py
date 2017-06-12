"""Test BoB Validation API"""

import unittest
import logging
import json
from typing import Dict, List
from bobby_client.env import TestEnvironment


class TestValidationAPIwithEvents(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()
        self.session = self.env.get_session()
        self.env.authenticate(self.session, api='validation')

    def tearDown(self):
        self.session.close()
        self.env.close()

    def submit_event(self, event: Dict, request_uri: str, expected_status: int):
        """Submit ticket events"""
        logging.info("Submitting %s", event['test_description'])
        del event['test_description']
        logging.debug(str(event))
        response = self.session.post("{}/{}".format(request_uri, event['ticketId']), json=event)
        if response.status_code != expected_status:
            logging.error(response.text)
        self.assertEqual(response.status_code, expected_status)
        logging.debug(response.json())

    def test_good_events(self):
        """Test good ticket event submission"""
        request_uri = '{}/validation'.format(self.env.endpoint('validation'))
        filename = self.env.config['test']['validation']['good_events']
        with open(filename) as events_file:
            events = json.load(events_file)
        for event in events:
            if not 'eventType' in event:
                event['eventType'] = 'validation'
            self.submit_event(self.env.update_dict_macros(event), request_uri, 201)

    def test_good_events_report(self):
        """Test good ticket event report submission"""
        request_uri = '{}/validation'.format(self.env.endpoint('validation'))
        filename = self.env.config['test']['validation']['good_events']
        with open(filename) as events_file:
            events = json.load(events_file)
        report = []
        for event in events:
            if not 'eventType' in event:
                event['eventType'] = 'validation'
            del event['test_description']
            report.append(self.env.update_dict_macros(event))
        response = self.session.post(request_uri, json=report)
        if response.status_code != 201:
            logging.error(response.text)
        self.assertEqual(response.status_code, 201)
        logging.debug(response.text)

    def test_bad_events(self):
        """Test bad ticket event submission"""
        request_uri = '{}/validation'.format(self.env.endpoint('validation'))
        filename = self.env.config['test']['validation']['bad_events']
        with open(filename) as events_file:
            events = json.load(events_file)
        for event in events:
            if not 'eventType' in event:
                event['eventType'] = 'validation'
            self.submit_event(self.env.update_dict_macros(event), request_uri, 400)


if __name__ == '__main__':
    unittest.main()
