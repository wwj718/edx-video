# pylint: disable=C0111
# pylint: disable=W0621

from lettuce import world
from .factories import *
from django.conf import settings
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from student.models import CourseEnrollment
from xmodule.modulestore.django import modulestore
from xmodule.contentstore.django import contentstore
from urllib import quote_plus


@world.absorb
def create_user(uname, password):

    # If the user already exists, don't try to create it again
    if len(User.objects.filter(username=uname)) > 0:
        return

    portal_user = UserFactory.build(username=uname, email=uname + '@edx.org')
    portal_user.set_password(password)
    portal_user.save()

    registration = world.RegistrationFactory(user=portal_user)
    registration.register(portal_user)
    registration.activate()

    user_profile = world.UserProfileFactory(user=portal_user)


@world.absorb
def log_in(username='robot', password='test', email='robot@edx.org', name='Robot'):
    """
    Use the auto_auth feature to programmatically log the user in
    """
    url = '/auto_auth?username=%s&password=%s&name=%s&email=%s' % (username,
          password, name, email)
    world.visit(url)

    # Save the user info in the world scenario_dict for use in the tests
    user = User.objects.get(username=username)
    world.scenario_dict['USER'] = user


@world.absorb
def register_by_course_id(course_id, is_staff=False):
    create_user('robot', 'password')
    u = User.objects.get(username='robot')
    if is_staff:
        u.is_staff = True
        u.save()
    CourseEnrollment.enroll(u, course_id)


@world.absorb
def clear_courses():
    # Flush and initialize the module store
    # It needs the templates because it creates new records
    # by cloning from the template.
    # Note that if your test module gets in some weird state
    # (though it shouldn't), do this manually
    # from the bash shell to drop it:
    # $ mongo test_xmodule --eval "db.dropDatabase()"
    modulestore().collection.drop()
    contentstore().fs_files.drop()
