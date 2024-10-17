import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import logging
from Tennis.utils import ask_MapBox_for_travel_time, check_if_enough_time
from Tennis.models import Game, Court

# Set up logger
logger = logging.getLogger('Tennis.tests')
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        logger.debug(f"\n----------------------------------------------------------------------\nPoczątek testu: {self._testMethodName}\n----------------------------------------------------------------------")

    @patch('Tennis.utils.requests.get')
    def test_ask_MapBox_for_travel_time(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'routes': [{'duration': 1800}]}
        mock_get.return_value = mock_response

        travel_time = ask_MapBox_for_travel_time(52.2297, 21.0122, 51.5074, -0.1278, 'mock-api-key')
        logger.debug(f"Oczekiwany czas dojazdu: 30 minut, otrzymany czas dojazdu w minutach: {travel_time}\n")
        self.assertEqual(travel_time, 30)

        mock_response.status_code = 500
        mock_response.json.return_value = {'message': 'Internal Server Error'}
        mock_get.return_value = mock_response

        travel_time = ask_MapBox_for_travel_time(52.2297, 21.0122, 51.5074, -0.1278, 'mock-api-key')
        logger.warning("This is an expected error case due to an API failure (500 response).")
        logger.debug(f"Oczekiwano: None, Otrzymano: {travel_time}\n")
        self.assertIsNone(travel_time)

        mock_response.status_code = 200
        mock_response.json.return_value = {'routes': []}
        mock_get.return_value = mock_response

        travel_time = ask_MapBox_for_travel_time(52.2297, 21.0122, 51.5074, -0.1278, 'mock-api-key')
        logger.info("No routes returned, which is expected due to an empty response from the API.")
        logger.debug(f"Oczekiwano: None, otrzymano: {travel_time}\n")
        self.assertIsNone(travel_time)
    # #
    @patch('Tennis.utils.ask_MapBox_for_travel_time', return_value=15)
    def test_check_if_enough_time(self, mock_travel_time):
        event_end_time = datetime.now()
        next_event_start_time = event_end_time + timedelta(minutes=30)
        event_court = MagicMock(court_id=1, latitude=52.2297, longitude=21.0122)
        next_event_court = MagicMock(court_id=2, latitude=51.5074, longitude=-0.1278)

        travel_time, time_available, alert = check_if_enough_time(
            event_end_time, next_event_start_time, event_court, next_event_court)

        logger.debug(f"Travel time: {travel_time}, Time available: {time_available}, Alert: {alert}")
        self.assertEqual(travel_time, 15)
        self.assertEqual(time_available, 30)
        self.assertFalse(alert)

        next_event_start_time = event_end_time + timedelta(minutes=10)

        travel_time, time_available, alert = check_if_enough_time(
            event_end_time, next_event_start_time, event_court, next_event_court)

        logger.warning("This is an expected alert case where travel time exceeds available time.")
        logger.debug(f"Travel time: {travel_time}, Time available: {time_available}, Alert: {alert}")
        self.assertEqual(travel_time, 15)
        self.assertEqual(time_available, 10)
        self.assertTrue(alert)

        next_event_court = event_court

        travel_time, time_available, alert = check_if_enough_time(
            event_end_time, next_event_start_time, event_court, next_event_court)

        logger.debug(f"Travel time: {travel_time}, Time available: {time_available}, Alert: {alert}")
        self.assertIsNone(travel_time)
        self.assertEqual(time_available, 10)
        self.assertFalse(alert)

if __name__ == '__main__':
    unittest.main()
