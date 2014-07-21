import unittest
import datetime

from fs.memoryfs import MemoryFS

from mock import Mock, patch

from xmodule.modulestore.xml import ImportSystem, XMLModuleStore
import xmodule.course_module
from django.utils.timezone import UTC


ORG = 'test_org'
COURSE = 'test_course'

NOW = datetime.datetime.strptime('2013-01-01T01:00:00', '%Y-%m-%dT%H:%M:00').replace(tzinfo=UTC())


class DummySystem(ImportSystem):
    @patch('xmodule.modulestore.xml.OSFS', lambda dir: MemoryFS())
    def __init__(self, load_error_modules):

        xmlstore = XMLModuleStore("data_dir", course_dirs=[],
                                  load_error_modules=load_error_modules)
        course_id = "/".join([ORG, COURSE, 'test_run'])
        course_dir = "test_dir"
        policy = {}
        error_tracker = Mock()
        parent_tracker = Mock()

        super(DummySystem, self).__init__(
            xmlstore,
            course_id,
            course_dir,
            policy,
            error_tracker,
            parent_tracker,
            load_error_modules=load_error_modules,
        )


def get_dummy_course(start, announcement=None, is_new=None, advertised_start=None, end=None):
    """Get a dummy course"""

    system = DummySystem(load_error_modules=True)

    def to_attrb(n, v):
        return '' if v is None else '{0}="{1}"'.format(n, v).lower()

    is_new = to_attrb('is_new', is_new)
    announcement = to_attrb('announcement', announcement)
    advertised_start = to_attrb('advertised_start', advertised_start)
    end = to_attrb('end', end)

    start_xml = '''
         <course org="{org}" course="{course}" display_organization="{org}_display" display_coursenumber="{course}_display"
                graceperiod="1 day" url_name="test"
                start="{start}"
                {announcement}
                {is_new}
                {advertised_start}
                {end}>
            <chapter url="hi" url_name="ch" display_name="CH">
                <html url_name="h" display_name="H">Two houses, ...</html>
            </chapter>
         </course>
         '''.format(org=ORG, course=COURSE, start=start, is_new=is_new,
        announcement=announcement, advertised_start=advertised_start, end=end)

    return system.process_xml(start_xml)


class IsNewCourseTestCase(unittest.TestCase):
    """Make sure the property is_new works on courses"""

    def setUp(self):
        # Needed for test_is_newish
        datetime_patcher = patch.object(
            xmodule.course_module, 'datetime',
            Mock(wraps=datetime.datetime)
        )
        mocked_datetime = datetime_patcher.start()
        mocked_datetime.now.return_value = NOW
        self.addCleanup(datetime_patcher.stop)

    @patch('xmodule.course_module.datetime.now')
    def test_sorting_score(self, gmtime_mock):
        gmtime_mock.return_value = NOW

        day1 = '2012-01-01T12:00'
        day2 = '2012-01-02T12:00'

        dates = [
            # Announce date takes priority over actual start
            # and courses announced on a later date are newer
            # than courses announced for an earlier date
            ((day1, day2, None), (day1, day1, None), self.assertLess),
            ((day1, day1, None), (day2, day1, None), self.assertEqual),

            # Announce dates take priority over advertised starts
            ((day1, day2, day1), (day1, day1, day1), self.assertLess),
            ((day1, day1, day2), (day2, day1, day2), self.assertEqual),

            # Later start == newer course
            ((day2, None, None), (day1, None, None), self.assertLess),
            ((day1, None, None), (day1, None, None), self.assertEqual),

            # Non-parseable advertised starts are ignored in preference to actual starts
            ((day2, None, "Spring"), (day1, None, "Fall"), self.assertLess),
            ((day1, None, "Spring"), (day1, None, "Fall"), self.assertEqual),

            # Partially parsable advertised starts should take priority over start dates
            ((day2, None, "October 2013"), (day2, None, "October 2012"), self.assertLess),
            ((day2, None, "October 2013"), (day1, None, "October 2013"), self.assertEqual),

            # Parseable advertised starts take priority over start dates
            ((day1, None, day2), (day1, None, day1), self.assertLess),
            ((day2, None, day2), (day1, None, day2), self.assertEqual),
        ]

        for a, b, assertion in dates:
            a_score = get_dummy_course(start=a[0], announcement=a[1], advertised_start=a[2]).sorting_score
            b_score = get_dummy_course(start=b[0], announcement=b[1], advertised_start=b[2]).sorting_score
            print "Comparing %s to %s" % (a, b)
            assertion(a_score, b_score)

    @patch('xmodule.course_module.datetime.now')
    def test_start_date_text(self, gmtime_mock):
        gmtime_mock.return_value = NOW

        settings = [
            # start, advertized, result
            ('2012-12-02T12:00', None, 'Dec 02, 2012'),
            ('2012-12-02T12:00', '2011-11-01T12:00', 'Nov 01, 2011'),
            ('2012-12-02T12:00', 'Spring 2012', 'Spring 2012'),
            ('2012-12-02T12:00', 'November, 2011', 'November, 2011'),
        ]

        for s in settings:
            d = get_dummy_course(start=s[0], advertised_start=s[1])
            print "Checking start=%s advertised=%s" % (s[0], s[1])
            self.assertEqual(d.start_date_text, s[2])

    def test_display_organization(self):
        descriptor = get_dummy_course(start='2012-12-02T12:00', is_new=True)
        self.assertNotEqual(descriptor.location.org, descriptor.display_org_with_default)
        self.assertEqual(descriptor.display_org_with_default, "{0}_display".format(ORG))

    def test_display_coursenumber(self):
        descriptor = get_dummy_course(start='2012-12-02T12:00', is_new=True)
        self.assertNotEqual(descriptor.location.course, descriptor.display_number_with_default)
        self.assertEqual(descriptor.display_number_with_default, "{0}_display".format(COURSE))

    def test_is_newish(self):
        descriptor = get_dummy_course(start='2012-12-02T12:00', is_new=True)
        assert(descriptor.is_newish is True)

        descriptor = get_dummy_course(start='2013-02-02T12:00', is_new=False)
        assert(descriptor.is_newish is False)

        descriptor = get_dummy_course(start='2013-02-02T12:00', is_new=True)
        assert(descriptor.is_newish is True)

        descriptor = get_dummy_course(start='2013-01-15T12:00')
        assert(descriptor.is_newish is True)

        descriptor = get_dummy_course(start='2013-03-01T12:00')
        assert(descriptor.is_newish is True)

        descriptor = get_dummy_course(start='2012-10-15T12:00')
        assert(descriptor.is_newish is False)

        descriptor = get_dummy_course(start='2012-12-31T12:00')
        assert(descriptor.is_newish is True)

    def test_end_date_text(self):
        # No end date set, returns empty string.
        d = get_dummy_course('2012-12-02T12:00')
        self.assertEqual('', d.end_date_text)

        d = get_dummy_course('2012-12-02T12:00', end='2014-9-04T12:00')
        self.assertEqual('Sep 04, 2014', d.end_date_text)


class DiscussionTopicsTestCase(unittest.TestCase):
    def test_default_discussion_topics(self):
        d = get_dummy_course('2012-12-02T12:00')
        self.assertEqual({'General': {'id': 'i4x-test_org-test_course-course-test'}}, d.discussion_topics)
