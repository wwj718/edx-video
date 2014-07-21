"""Tests for classes defined in fields.py."""
import datetime
import unittest
from django.utils.timezone import UTC
from xmodule.fields import Date, Timedelta
from xmodule.timeinfo import TimeInfo
import time


class DateTest(unittest.TestCase):
    date = Date()

    def compare_dates(self, dt1, dt2, expected_delta):
        self.assertEqual(dt1 - dt2, expected_delta, str(dt1) + "-"
                                                    + str(dt2) + "!=" + str(expected_delta))

    def test_from_json(self):
        '''Test conversion from iso compatible date strings to struct_time'''
        self.compare_dates(
            DateTest.date.from_json("2013-01-01"),
            DateTest.date.from_json("2012-12-31"),
            datetime.timedelta(days=1))
        self.compare_dates(
            DateTest.date.from_json("2013-01-01T00"),
            DateTest.date.from_json("2012-12-31T23"),
            datetime.timedelta(hours=1))
        self.compare_dates(
            DateTest.date.from_json("2013-01-01T00:00"),
            DateTest.date.from_json("2012-12-31T23:59"),
            datetime.timedelta(minutes=1))
        self.compare_dates(
            DateTest.date.from_json("2013-01-01T00:00:00"),
            DateTest.date.from_json("2012-12-31T23:59:59"),
            datetime.timedelta(seconds=1))
        self.compare_dates(
            DateTest.date.from_json("2013-01-01T00:00:00Z"),
            DateTest.date.from_json("2012-12-31T23:59:59Z"),
            datetime.timedelta(seconds=1))
        self.compare_dates(
            DateTest.date.from_json("2012-12-31T23:00:01-01:00"),
            DateTest.date.from_json("2013-01-01T00:00:00+01:00"),
            datetime.timedelta(hours=1, seconds=1))

    def test_return_None(self):
        self.assertIsNone(DateTest.date.from_json(""))
        self.assertIsNone(DateTest.date.from_json(None))
        with self.assertRaises(TypeError):
            DateTest.date.from_json(['unknown value'])

    def test_old_due_date_format(self):
        current = datetime.datetime.today()
        self.assertEqual(
            datetime.datetime(current.year, 3, 12, 12, tzinfo=UTC()),
            DateTest.date.from_json("March 12 12:00"))
        self.assertEqual(
            datetime.datetime(current.year, 12, 4, 16, 30, tzinfo=UTC()),
            DateTest.date.from_json("December 4 16:30"))
        self.assertIsNone(DateTest.date.from_json("12 12:00"))

    def test_non_std_from_json(self):
        """
        Test the non-standard args being passed to from_json
        """
        now = datetime.datetime.now(UTC())
        delta = now - datetime.datetime.fromtimestamp(0, UTC())
        self.assertEqual(DateTest.date.from_json(delta.total_seconds() * 1000),
            now)
        yesterday = datetime.datetime.now(UTC()) - datetime.timedelta(days=-1)
        self.assertEqual(DateTest.date.from_json(yesterday), yesterday)

    def test_to_json(self):
        '''
        Test converting time reprs to iso dates
        '''
        self.assertEqual(
            DateTest.date.to_json(
                datetime.datetime.strptime("2012-12-31T23:59:59Z", "%Y-%m-%dT%H:%M:%SZ")),
            "2012-12-31T23:59:59Z")
        self.assertEqual(
            DateTest.date.to_json(
                DateTest.date.from_json("2012-12-31T23:59:59Z")),
            "2012-12-31T23:59:59Z")
        self.assertEqual(
            DateTest.date.to_json(
                DateTest.date.from_json("2012-12-31T23:00:01-01:00")),
            "2012-12-31T23:00:01-01:00")
        with self.assertRaises(TypeError):
            DateTest.date.to_json('2012-12-31T23:00:01-01:00')


class TimedeltaTest(unittest.TestCase):
    delta = Timedelta()

    def test_from_json(self):
        self.assertEqual(
            TimedeltaTest.delta.from_json('1 day 12 hours 59 minutes 59 seconds'),
            datetime.timedelta(days=1, hours=12, minutes=59, seconds=59)
        )

        self.assertEqual(
            TimedeltaTest.delta.from_json('1 day 46799 seconds'),
            datetime.timedelta(days=1, seconds=46799)
        )

    def test_to_json(self):
        self.assertEqual(
            '1 days 46799 seconds',
            TimedeltaTest.delta.to_json(datetime.timedelta(days=1, hours=12, minutes=59, seconds=59))
        )


class TimeInfoTest(unittest.TestCase):
    def test_time_info(self):
        due_date = datetime.datetime(2000, 4, 14, 10, tzinfo=UTC())
        grace_pd_string = '1 day 12 hours 59 minutes 59 seconds'
        timeinfo = TimeInfo(due_date, grace_pd_string)
        self.assertEqual(timeinfo.close_date,
            due_date + Timedelta().from_json(grace_pd_string))
