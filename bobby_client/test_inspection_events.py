"""Test BoB Inspection API"""

import unittest
import logging
import json
from typing import Dict
from bobby_client.env import TestEnvironment


class TestInspectionAPIwithEvents(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.env = TestEnvironment.create_from_config_file()
        self.session = self.env.get_session()
        self.env.authenticate(self.session, api='inspection')

    def tearDown(self):
        self.session.close()
        self.env.close()

    def _submit_event(self, event: Dict, request_uri: str, expected_status: int):
        """Submit ticket events"""
        logging.info("Submitting %s", event['test_description'])
        del event['test_description']
        response = self.session.post("{}/{}".format(request_uri, event['ticketId']), json=event)
        self.assertEqual(response.status_code, expected_status)

    def test_good_events(self):
        """Test good ticket event submission"""
        request_uri = '{}/inspection'.format(self.env.endpoint('inspection'))
        filename = self.env.config['test']['inspection']['good_events']
        with open(filename) as events_file:
            events = json.load(events_file)
        for event in events:
            if 'eventType' not in event:
                event['eventType'] = 'inspection'
            self._submit_event(self.env.update_dict_macros(event), request_uri, 201)

    def test_good_events_report(self):
        """Test good ticket event report submission"""
        request_uri = '{}/inspection'.format(self.env.endpoint('inspection'))
        filename = self.env.config['test']['inspection']['good_events']
        with open(filename) as events_file:
            events = json.load(events_file)
        report = []
        for event in events:
            if 'eventType' not in event:
                event['eventType'] = 'inspection'
            del event['test_description']
            report.append(self.env.update_dict_macros(event))
        response = self.session.post(request_uri, json=report)
        self.assertEqual(response.status_code, 200)

    def test_bad_events(self):
        """Test bad ticket event submission"""
        request_uri = '{}/inspection'.format(self.env.endpoint('inspection'))
        filename = self.env.config['test']['inspection']['bad_events']
        with open(filename) as events_file:
            events = json.load(events_file)
        for event in events:
            if 'eventType' not in event:
                event['eventType'] = 'inspection'
            self._submit_event(self.env.update_dict_macros(event), request_uri, 400)


if __name__ == '__main__':
    unittest.main()
