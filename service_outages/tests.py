import datetime
import pytz

from django.test import TestCase
from service_outages.views import ServiceOutageRecordView


class ServiceFlappingTest(TestCase):
    """Test module for Service Flapping"""

    def setUp(self):
        """Create testing dataset.

        The dataset is a dictionary of services where the keys
        are the service ids, and the value is another dictionary
        containing duration, start time and end time lists.
        """
        self.test_view = ServiceOutageRecordView()

        self.test_services_dict = {
            # The following services must be in the flapping results:

            # The sum of outages equals 15 minutes in the 2-hour interval
            'exact_outage_sum': {
                'duration': [3, 9, 3],
                'start_time': [
                    datetime.datetime(2019, 7, 15, 4, 18, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 44, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 5, 18, 19, tzinfo=pytz.utc)],
                'end_time': [
                    datetime.datetime(2019, 7, 15, 4, 21, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 53, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 5, 21, 19, tzinfo=pytz.utc)]},
            # Second outage is longer than 15 minutes
            'individual_outage_match': {
                'duration': [9, 16, 5],
                'start_time': [
                    datetime.datetime(2019, 7, 15, 4, 18, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 44, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 7, 18, 19, tzinfo=pytz.utc)],
                'end_time': [
                    datetime.datetime(2019, 7, 15, 4, 27, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 5, 00, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 7, 23, 19, tzinfo=pytz.utc)]},
            # Second and third outage combined are exactly 119 minutes within a 2-hour interval
            'partial_outage_match': {
                'duration': [5, 9, 110],
                'start_time': [
                    datetime.datetime(2019, 7, 13, 7, 18, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 18, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 28, 19, tzinfo=pytz.utc)],
                'end_time': [
                    datetime.datetime(2019, 7, 13, 7, 23, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 27, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 6, 18, 19, tzinfo=pytz.utc)]},

            # The following services must not be in the flapping results:

            # The service outage is longer than the flap interval
            'long_outage': {
                'duration': [2, 122],
                'start_time': [
                    datetime.datetime(2019, 7, 15, 4, 18, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 40, 19, tzinfo=pytz.utc)],
                'end_time': [
                    datetime.datetime(2019, 7, 15, 4, 20, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 6, 42, 19, tzinfo=pytz.utc)]},
            # Outage duration is 15 minutes, but it is just one outage in the 2-hour interval
            'single_exact_outage': {
                'duration': [15],
                'start_time': [datetime.datetime(2019, 7, 15, 4, 18, 19, tzinfo=pytz.utc)],
                'end_time': [datetime.datetime(2019, 7, 15, 4, 33, 19, tzinfo=pytz.utc)]},
            # Service has shorter outages, the sum is less than 15 minutes
            'shorter_outage_sum': {
                'duration': [3, 5],
                'start_time': [
                    datetime.datetime(2019, 7, 15, 4, 18, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 44, 19, tzinfo=pytz.utc)],
                'end_time': [
                    datetime.datetime(2019, 7, 15, 4, 21, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 4, 49, 19, tzinfo=pytz.utc)]},
            # The sum of outages is between 15 and 120 minutes but it exits the 2-hour flap interval
            'outage_sum_outside_flap_interval': {
                'duration': [40, 9, 5],
                'start_time': [
                    datetime.datetime(2019, 7, 15, 4, 18, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 7, 44, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 8, 18, 19, tzinfo=pytz.utc)],
                'end_time': [
                    datetime.datetime(2019, 7, 15, 4, 58, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 7, 53, 19, tzinfo=pytz.utc),
                    datetime.datetime(2019, 7, 15, 8, 23, 19, tzinfo=pytz.utc)]},
        }

    def test_detect_flapping_scenarios(self):
        result = self.test_view.detect_flapping_scenarios(self.test_services_dict)
        self.assertIn('exact_outage_sum', result)
        self.assertIn('individual_outage_match', result)
        self.assertIn('partial_outage_match', result)
        self.assertNotIn('long_outage', result)
        self.assertNotIn('single_exact_outage', result)
        self.assertNotIn('shorter_outage_sum', result)
        self.assertNotIn('outage_sum_outside_flap_interval', result)
