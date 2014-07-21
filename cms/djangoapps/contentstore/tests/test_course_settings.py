"""
Tests for Studio Course Settings.
"""
import datetime
import json
import copy
import mock

from django.core.urlresolvers import reverse
from django.utils.timezone import UTC
from django.test.utils import override_settings

from xmodule.modulestore import Location
from models.settings.course_details import (CourseDetails, CourseSettingsEncoder)
from models.settings.course_grading import CourseGradingModel
from contentstore.utils import get_modulestore
from xmodule.modulestore.tests.factories import CourseFactory


from models.settings.course_metadata import CourseMetadata
from xmodule.fields import Date

from .utils import CourseTestCase


class CourseDetailsTestCase(CourseTestCase):
    """
    Tests the first course settings page (course dates, overview, etc.).
    """
    def test_virgin_fetch(self):
        details = CourseDetails.fetch(self.course.location)
        self.assertEqual(details.course_location, self.course.location, "Location not copied into")
        self.assertIsNotNone(details.start_date.tzinfo)
        self.assertIsNone(details.end_date, "end date somehow initialized " + str(details.end_date))
        self.assertIsNone(details.enrollment_start, "enrollment_start date somehow initialized " + str(details.enrollment_start))
        self.assertIsNone(details.enrollment_end, "enrollment_end date somehow initialized " + str(details.enrollment_end))
        self.assertIsNone(details.syllabus, "syllabus somehow initialized" + str(details.syllabus))
        self.assertIsNone(details.intro_video, "intro_video somehow initialized" + str(details.intro_video))
        self.assertIsNone(details.effort, "effort somehow initialized" + str(details.effort))

    def test_encoder(self):
        details = CourseDetails.fetch(self.course.location)
        jsondetails = json.dumps(details, cls=CourseSettingsEncoder)
        jsondetails = json.loads(jsondetails)
        self.assertTupleEqual(Location(jsondetails['course_location']), self.course.location, "Location !=")
        self.assertIsNone(jsondetails['end_date'], "end date somehow initialized ")
        self.assertIsNone(jsondetails['enrollment_start'], "enrollment_start date somehow initialized ")
        self.assertIsNone(jsondetails['enrollment_end'], "enrollment_end date somehow initialized ")
        self.assertIsNone(jsondetails['syllabus'], "syllabus somehow initialized")
        self.assertIsNone(jsondetails['intro_video'], "intro_video somehow initialized")
        self.assertIsNone(jsondetails['effort'], "effort somehow initialized")

    def test_ooc_encoder(self):
        """
        Test the encoder out of its original constrained purpose to see if it functions for general use
        """
        details = {
            'location': Location(['tag', 'org', 'course', 'category', 'name']),
            'number': 1,
            'string': 'string',
            'datetime': datetime.datetime.now(UTC())
        }
        jsondetails = json.dumps(details, cls=CourseSettingsEncoder)
        jsondetails = json.loads(jsondetails)

        self.assertIn('location', jsondetails)
        self.assertIn('org', jsondetails['location'])
        self.assertEquals('org', jsondetails['location'][1])
        self.assertEquals(1, jsondetails['number'])
        self.assertEqual(jsondetails['string'], 'string')

    def test_update_and_fetch(self):
        jsondetails = CourseDetails.fetch(self.course.location)
        jsondetails.syllabus = "<a href='foo'>bar</a>"
        # encode - decode to convert date fields and other data which changes form
        self.assertEqual(
            CourseDetails.update_from_json(jsondetails.__dict__).syllabus,
            jsondetails.syllabus, "After set syllabus"
        )
        jsondetails.overview = "Overview"
        self.assertEqual(
            CourseDetails.update_from_json(jsondetails.__dict__).overview,
            jsondetails.overview, "After set overview"
        )
        jsondetails.intro_video = "intro_video"
        self.assertEqual(
            CourseDetails.update_from_json(jsondetails.__dict__).intro_video,
            jsondetails.intro_video, "After set intro_video"
        )
        jsondetails.effort = "effort"
        self.assertEqual(
            CourseDetails.update_from_json(jsondetails.__dict__).effort,
            jsondetails.effort, "After set effort"
        )
        jsondetails.start_date = datetime.datetime(2010, 10, 1, 0, tzinfo=UTC())
        self.assertEqual(
            CourseDetails.update_from_json(jsondetails.__dict__).start_date,
            jsondetails.start_date
        )

    @override_settings(MKTG_URLS={'ROOT': 'dummy-root'})
    def test_marketing_site_fetch(self):
        settings_details_url = reverse(
            'settings_details',
            kwargs={
                'org': self.course.location.org,
                'name': self.course.location.name,
                'course': self.course.location.course
            }
        )

        with mock.patch.dict('django.conf.settings.MITX_FEATURES', {'ENABLE_MKTG_SITE': True}):
            response = self.client.get(settings_details_url)
            self.assertContains(response, "Course Summary Page")
            self.assertContains(response, "course summary page will not be viewable")

            self.assertContains(response, "Course Start Date")
            self.assertContains(response, "Course End Date")
            self.assertNotContains(response, "Enrollment Start Date")
            self.assertNotContains(response, "Enrollment End Date")
            self.assertContains(response, "not the dates shown on your course summary page")

            self.assertNotContains(response, "Introducing Your Course")
            self.assertNotContains(response, "Requirements")

    def test_regular_site_fetch(self):
        settings_details_url = reverse(
            'settings_details',
            kwargs={
                'org': self.course.location.org,
                'name': self.course.location.name,
                'course': self.course.location.course
            }
        )

        with mock.patch.dict('django.conf.settings.MITX_FEATURES', {'ENABLE_MKTG_SITE': False}):
            response = self.client.get(settings_details_url)
            self.assertContains(response, "Course Summary Page")
            self.assertNotContains(response, "course summary page will not be viewable")

            self.assertContains(response, "Course Start Date")
            self.assertContains(response, "Course End Date")
            self.assertContains(response, "Enrollment Start Date")
            self.assertContains(response, "Enrollment End Date")
            self.assertNotContains(response, "not the dates shown on your course summary page")

            self.assertContains(response, "Introducing Your Course")
            self.assertContains(response, "Requirements")


class CourseDetailsViewTest(CourseTestCase):
    """
    Tests for modifying content on the first course settings page (course dates, overview, etc.).
    """
    def alter_field(self, url, details, field, val):
        setattr(details, field, val)
        # Need to partially serialize payload b/c the mock doesn't handle it correctly
        payload = copy.copy(details.__dict__)
        payload['course_location'] = details.course_location.url()
        payload['start_date'] = CourseDetailsViewTest.convert_datetime_to_iso(details.start_date)
        payload['end_date'] = CourseDetailsViewTest.convert_datetime_to_iso(details.end_date)
        payload['enrollment_start'] = CourseDetailsViewTest.convert_datetime_to_iso(details.enrollment_start)
        payload['enrollment_end'] = CourseDetailsViewTest.convert_datetime_to_iso(details.enrollment_end)
        resp = self.client.post(url, json.dumps(payload), "application/json")
        self.compare_details_with_encoding(json.loads(resp.content), details.__dict__, field + str(val))

    @staticmethod
    def convert_datetime_to_iso(datetime_obj):
        return Date().to_json(datetime_obj)

    def test_update_and_fetch(self):
        loc = self.course.location
        details = CourseDetails.fetch(loc)

        # resp s/b json from here on
        url = reverse('course_settings', kwargs={'org': loc.org, 'course': loc.course,
                                                 'name': loc.name, 'section': 'details'})
        resp = self.client.get(url)
        self.compare_details_with_encoding(json.loads(resp.content), details.__dict__, "virgin get")

        utc = UTC()
        self.alter_field(url, details, 'start_date', datetime.datetime(2012, 11, 12, 1, 30, tzinfo=utc))
        self.alter_field(url, details, 'start_date', datetime.datetime(2012, 11, 1, 13, 30, tzinfo=utc))
        self.alter_field(url, details, 'end_date', datetime.datetime(2013, 2, 12, 1, 30, tzinfo=utc))
        self.alter_field(url, details, 'enrollment_start', datetime.datetime(2012, 10, 12, 1, 30, tzinfo=utc))

        self.alter_field(url, details, 'enrollment_end', datetime.datetime(2012, 11, 15, 1, 30, tzinfo=utc))
        self.alter_field(url, details, 'overview', "Overview")
        self.alter_field(url, details, 'intro_video', "intro_video")
        self.alter_field(url, details, 'effort', "effort")

    def compare_details_with_encoding(self, encoded, details, context):
        self.compare_date_fields(details, encoded, context, 'start_date')
        self.compare_date_fields(details, encoded, context, 'end_date')
        self.compare_date_fields(details, encoded, context, 'enrollment_start')
        self.compare_date_fields(details, encoded, context, 'enrollment_end')
        self.assertEqual(details['overview'], encoded['overview'], context + " overviews not ==")
        self.assertEqual(details['intro_video'], encoded.get('intro_video', None), context + " intro_video not ==")
        self.assertEqual(details['effort'], encoded['effort'], context + " efforts not ==")

    def compare_date_fields(self, details, encoded, context, field):
        if details[field] is not None:
            date = Date()
            if field in encoded and encoded[field] is not None:
                dt1 = date.from_json(encoded[field])
                dt2 = details[field]

                self.assertEqual(dt1, dt2, msg="{} != {} at {}".format(dt1, dt2, context))
            else:
                self.fail(field + " missing from encoded but in details at " + context)
        elif field in encoded and encoded[field] is not None:
            self.fail(field + " included in encoding but missing from details at " + context)


class CourseGradingTest(CourseTestCase):
    """
    Tests for the course settings grading page.
    """
    def test_initial_grader(self):
        descriptor = get_modulestore(self.course.location).get_item(self.course.location)
        test_grader = CourseGradingModel(descriptor)
        # ??? How much should this test bake in expectations about defaults and thus fail if defaults change?
        self.assertEqual(self.course.location, test_grader.course_location, "Course locations")
        self.assertIsNotNone(test_grader.graders, "No graders")
        self.assertIsNotNone(test_grader.grade_cutoffs, "No cutoffs")

    def test_fetch_grader(self):
        test_grader = CourseGradingModel.fetch(self.course.location.url())
        self.assertEqual(self.course.location, test_grader.course_location, "Course locations")
        self.assertIsNotNone(test_grader.graders, "No graders")
        self.assertIsNotNone(test_grader.grade_cutoffs, "No cutoffs")

        test_grader = CourseGradingModel.fetch(self.course.location)
        self.assertEqual(self.course.location, test_grader.course_location, "Course locations")
        self.assertIsNotNone(test_grader.graders, "No graders")
        self.assertIsNotNone(test_grader.grade_cutoffs, "No cutoffs")

        for i, grader in enumerate(test_grader.graders):
            subgrader = CourseGradingModel.fetch_grader(self.course.location, i)
            self.assertDictEqual(grader, subgrader, str(i) + "th graders not equal")

        subgrader = CourseGradingModel.fetch_grader(self.course.location.list(), 0)
        self.assertDictEqual(test_grader.graders[0], subgrader, "failed with location as list")

    def test_fetch_cutoffs(self):
        test_grader = CourseGradingModel.fetch_cutoffs(self.course.location)
        # ??? should this check that it's at least a dict? (expected is { "pass" : 0.5 } I think)
        self.assertIsNotNone(test_grader, "No cutoffs via fetch")

        test_grader = CourseGradingModel.fetch_cutoffs(self.course.location.url())
        self.assertIsNotNone(test_grader, "No cutoffs via fetch with url")

    def test_fetch_grace(self):
        test_grader = CourseGradingModel.fetch_grace_period(self.course.location)
        # almost a worthless test
        self.assertIn('grace_period', test_grader, "No grace via fetch")

        test_grader = CourseGradingModel.fetch_grace_period(self.course.location.url())
        self.assertIn('grace_period', test_grader, "No cutoffs via fetch with url")

    def test_update_from_json(self):
        test_grader = CourseGradingModel.fetch(self.course.location)
        altered_grader = CourseGradingModel.update_from_json(test_grader.__dict__)
        self.assertDictEqual(test_grader.__dict__, altered_grader.__dict__, "Noop update")

        test_grader.graders[0]['weight'] = test_grader.graders[0].get('weight') * 2
        altered_grader = CourseGradingModel.update_from_json(test_grader.__dict__)
        self.assertDictEqual(test_grader.__dict__, altered_grader.__dict__, "Weight[0] * 2")

        test_grader.grade_cutoffs['D'] = 0.3
        altered_grader = CourseGradingModel.update_from_json(test_grader.__dict__)
        self.assertDictEqual(test_grader.__dict__, altered_grader.__dict__, "cutoff add D")

        test_grader.grace_period = {'hours': 4, 'minutes': 5, 'seconds': 0}
        altered_grader = CourseGradingModel.update_from_json(test_grader.__dict__)
        self.assertDictEqual(test_grader.__dict__, altered_grader.__dict__, "4 hour grace period")

    def test_update_grader_from_json(self):
        test_grader = CourseGradingModel.fetch(self.course.location)
        altered_grader = CourseGradingModel.update_grader_from_json(test_grader.course_location, test_grader.graders[1])
        self.assertDictEqual(test_grader.graders[1], altered_grader, "Noop update")

        test_grader.graders[1]['min_count'] = test_grader.graders[1].get('min_count') + 2
        altered_grader = CourseGradingModel.update_grader_from_json(test_grader.course_location, test_grader.graders[1])
        self.assertDictEqual(test_grader.graders[1], altered_grader, "min_count[1] + 2")

        test_grader.graders[1]['drop_count'] = test_grader.graders[1].get('drop_count') + 1
        altered_grader = CourseGradingModel.update_grader_from_json(test_grader.course_location, test_grader.graders[1])
        self.assertDictEqual(test_grader.graders[1], altered_grader, "drop_count[1] + 2")

    def test_update_cutoffs_from_json(self):
        test_grader = CourseGradingModel.fetch(self.course.location)
        CourseGradingModel.update_cutoffs_from_json(test_grader.course_location, test_grader.grade_cutoffs)
        # Unlike other tests, need to actually perform a db fetch for this test since update_cutoffs_from_json
        #  simply returns the cutoffs you send into it, rather than returning the db contents.
        altered_grader = CourseGradingModel.fetch(self.course.location)
        self.assertDictEqual(test_grader.grade_cutoffs, altered_grader.grade_cutoffs, "Noop update")

        test_grader.grade_cutoffs['D'] = 0.3
        CourseGradingModel.update_cutoffs_from_json(test_grader.course_location, test_grader.grade_cutoffs)
        altered_grader = CourseGradingModel.fetch(self.course.location)
        self.assertDictEqual(test_grader.grade_cutoffs, altered_grader.grade_cutoffs, "cutoff add D")

        test_grader.grade_cutoffs['Pass'] = 0.75
        CourseGradingModel.update_cutoffs_from_json(test_grader.course_location, test_grader.grade_cutoffs)
        altered_grader = CourseGradingModel.fetch(self.course.location)
        self.assertDictEqual(test_grader.grade_cutoffs, altered_grader.grade_cutoffs, "cutoff change 'Pass'")

    def test_delete_grace_period(self):
        test_grader = CourseGradingModel.fetch(self.course.location)
        CourseGradingModel.update_grace_period_from_json(test_grader.course_location, test_grader.grace_period)
        # update_grace_period_from_json doesn't return anything, so query the db for its contents.
        altered_grader = CourseGradingModel.fetch(self.course.location)
        self.assertEqual(test_grader.grace_period, altered_grader.grace_period, "Noop update")

        test_grader.grace_period = {'hours': 15, 'minutes': 5, 'seconds': 30}
        CourseGradingModel.update_grace_period_from_json(test_grader.course_location, test_grader.grace_period)
        altered_grader = CourseGradingModel.fetch(self.course.location)
        self.assertDictEqual(test_grader.grace_period, altered_grader.grace_period, "Adding in a grace period")

        test_grader.grace_period = {'hours': 1, 'minutes': 10, 'seconds': 0}
        # Now delete the grace period
        CourseGradingModel.delete_grace_period(test_grader.course_location)
        # update_grace_period_from_json doesn't return anything, so query the db for its contents.
        altered_grader = CourseGradingModel.fetch(self.course.location)
        # Once deleted, the grace period should simply be None
        self.assertEqual(None, altered_grader.grace_period, "Delete grace period")

    def test_update_section_grader_type(self):
        # Get the descriptor and the section_grader_type and assert they are the default values
        descriptor = get_modulestore(self.course.location).get_item(self.course.location)
        section_grader_type = CourseGradingModel.get_section_grader_type(self.course.location)

        self.assertEqual('Not Graded', section_grader_type['graderType'])
        self.assertEqual(None, descriptor.lms.format)
        self.assertEqual(False, descriptor.lms.graded)

        # Change the default grader type to Homework, which should also mark the section as graded
        CourseGradingModel.update_section_grader_type(self.course.location, {'graderType': 'Homework'})
        descriptor = get_modulestore(self.course.location).get_item(self.course.location)
        section_grader_type = CourseGradingModel.get_section_grader_type(self.course.location)

        self.assertEqual('Homework', section_grader_type['graderType'])
        self.assertEqual('Homework', descriptor.lms.format)
        self.assertEqual(True, descriptor.lms.graded)

        # Change the grader type back to Not Graded, which should also unmark the section as graded
        CourseGradingModel.update_section_grader_type(self.course.location, {'graderType': 'Not Graded'})
        descriptor = get_modulestore(self.course.location).get_item(self.course.location)
        section_grader_type = CourseGradingModel.get_section_grader_type(self.course.location)

        self.assertEqual('Not Graded', section_grader_type['graderType'])
        self.assertEqual(None, descriptor.lms.format)
        self.assertEqual(False, descriptor.lms.graded)


class CourseMetadataEditingTest(CourseTestCase):
    """
    Tests for CourseMetadata.
    """
    def setUp(self):
        CourseTestCase.setUp(self)
        CourseFactory.create(org='edX', course='999', display_name='Robot Super Course')
        self.fullcourse_location = Location(['i4x', 'edX', '999', 'course', 'Robot_Super_Course', None])

    def test_fetch_initial_fields(self):
        test_model = CourseMetadata.fetch(self.course.location)
        self.assertIn('display_name', test_model, 'Missing editable metadata field')
        self.assertEqual(test_model['display_name'], 'Robot Super Course', "not expected value")

        test_model = CourseMetadata.fetch(self.fullcourse_location)
        self.assertNotIn('graceperiod', test_model, 'blacklisted field leaked in')
        self.assertIn('display_name', test_model, 'full missing editable metadata field')
        self.assertEqual(test_model['display_name'], 'Robot Super Course', "not expected value")
        self.assertIn('rerandomize', test_model, 'Missing rerandomize metadata field')
        self.assertIn('showanswer', test_model, 'showanswer field ')
        self.assertIn('xqa_key', test_model, 'xqa_key field ')

    def test_update_from_json(self):
        test_model = CourseMetadata.update_from_json(self.course.location, {
            "advertised_start": "start A",
            "testcenter_info": {"c": "test"},
            "days_early_for_beta": 2
        })
        self.update_check(test_model)
        # try fresh fetch to ensure persistence
        test_model = CourseMetadata.fetch(self.course.location)
        self.update_check(test_model)
        # now change some of the existing metadata
        test_model = CourseMetadata.update_from_json(self.course.location, {
            "advertised_start": "start B",
            "display_name": "jolly roger"}
        )
        self.assertIn('display_name', test_model, 'Missing editable metadata field')
        self.assertEqual(test_model['display_name'], 'jolly roger', "not expected value")
        self.assertIn('advertised_start', test_model, 'Missing revised advertised_start metadata field')
        self.assertEqual(test_model['advertised_start'], 'start B', "advertised_start not expected value")

    def update_check(self, test_model):
        self.assertIn('display_name', test_model, 'Missing editable metadata field')
        self.assertEqual(test_model['display_name'], 'Robot Super Course', "not expected value")
        self.assertIn('advertised_start', test_model, 'Missing new advertised_start metadata field')
        self.assertEqual(test_model['advertised_start'], 'start A', "advertised_start not expected value")
        self.assertIn('testcenter_info', test_model, 'Missing testcenter_info metadata field')
        self.assertDictEqual(test_model['testcenter_info'], {"c": "test"}, "testcenter_info not expected value")
        self.assertIn('days_early_for_beta', test_model, 'Missing days_early_for_beta metadata field')
        self.assertEqual(test_model['days_early_for_beta'], 2, "days_early_for_beta not expected value")

    def test_delete_key(self):
        test_model = CourseMetadata.delete_key(self.fullcourse_location, {'deleteKeys': ['doesnt_exist', 'showanswer', 'xqa_key']})
        # ensure no harm
        self.assertNotIn('graceperiod', test_model, 'blacklisted field leaked in')
        self.assertIn('display_name', test_model, 'full missing editable metadata field')
        self.assertEqual(test_model['display_name'], 'Robot Super Course', "not expected value")
        self.assertIn('rerandomize', test_model, 'Missing rerandomize metadata field')
        # check for deletion effectiveness
        self.assertEqual('finished', test_model['showanswer'], 'showanswer field still in')
        self.assertEqual(None, test_model['xqa_key'], 'xqa_key field still in')


class CourseGraderUpdatesTest(CourseTestCase):
    def setUp(self):
        super(CourseGraderUpdatesTest, self).setUp()
        self.url = reverse("course_settings", kwargs={
            'org': self.course.location.org,
            'course': self.course.location.course,
            'name': self.course.location.name,
            'grader_index': 0,
        })

    def test_get(self):
        resp = self.client.get(self.url)
        self.assert2XX(resp.status_code)
        obj = json.loads(resp.content)

    def test_delete(self):
        resp = self.client.delete(self.url)
        self.assert2XX(resp.status_code)

    def test_post(self):
        grader = {
            "type": "manual",
            "min_count": 5,
            "drop_count": 10,
            "short_label": "yo momma",
            "weight": 17.3,
        }
        resp = self.client.post(self.url, grader)
        self.assert2XX(resp.status_code)
        obj = json.loads(resp.content)
