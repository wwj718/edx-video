"""
Tests for instructor.basic
"""

from django.test import TestCase
from student.models import CourseEnrollment
from student.tests.factories import UserFactory

from analytics.basic import enrolled_students_features, AVAILABLE_FEATURES, STUDENT_FEATURES, PROFILE_FEATURES


class TestAnalyticsBasic(TestCase):
    """ Test basic analytics functions. """

    def setUp(self):
        self.course_id = 'some/robot/course/id'
        self.users = tuple(UserFactory() for _ in xrange(30))
        self.ces = tuple(CourseEnrollment.enroll(user, self.course_id)
                         for user in self.users)

    def test_enrolled_students_features_username(self):
        self.assertIn('username', AVAILABLE_FEATURES)
        userreports = enrolled_students_features(self.course_id, ['username'])
        self.assertEqual(len(userreports), len(self.users))
        for userreport in userreports:
            self.assertEqual(userreport.keys(), ['username'])
            self.assertIn(userreport['username'], [user.username for user in self.users])

    def test_enrolled_students_features_keys(self):
        query_features = ('username', 'name', 'email')
        for feature in query_features:
            self.assertIn(feature, AVAILABLE_FEATURES)
        userreports = enrolled_students_features(self.course_id, query_features)
        self.assertEqual(len(userreports), len(self.users))
        for userreport in userreports:
            self.assertEqual(set(userreport.keys()), set(query_features))
            self.assertIn(userreport['username'], [user.username for user in self.users])
            self.assertIn(userreport['email'], [user.email for user in self.users])
            self.assertIn(userreport['name'], [user.profile.name for user in self.users])

    def test_available_features(self):
        self.assertEqual(len(AVAILABLE_FEATURES), len(STUDENT_FEATURES + PROFILE_FEATURES))
        self.assertEqual(set(AVAILABLE_FEATURES), set(STUDENT_FEATURES + PROFILE_FEATURES))
