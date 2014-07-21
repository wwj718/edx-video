import re
from urlparse import urlparse

from django.http import Http404
from django.shortcuts import redirect

from wiki.models import reverse as wiki_reverse
from courseware.access import has_access
from courseware.courses import get_course_with_access


IN_COURSE_WIKI_REGEX = r'/courses/(?P<course_id>[^/]+/[^/]+/[^/]+)/wiki/(?P<wiki_path>.*|)$'


class Middleware(object):
    """
    This middleware is to keep the course nav bar above the wiki while
    the student clicks around to other wiki pages.
    If it intercepts a request for /wiki/.. that has a referrer in the
    form /courses/course_id/... it will redirect the user to the page
    /courses/course_id/wiki/...

    It is also possible that someone followed a link leading to a course
    that they don't have access to. In this case, we redirect them to the
    same page on the regular wiki.

    If we return a redirect, this middleware makes sure that the redirect
    keeps the student in the course.

    Finally, if the student is in the course viewing a wiki, we change the
    reverse() function to resolve wiki urls as a course wiki url by setting
    the _transform_url attribute on wiki.models.reverse.

    Forgive me Father, for I have hacked.
    """

    def __init__(self):
        self.redirected = False

    def process_request(self, request):
        self.redirected = False
        wiki_reverse._transform_url = lambda url: url

        referer = request.META.get('HTTP_REFERER')
        destination = request.path


        if request.method == 'GET':
            new_destination = self.get_redirected_url(request.user, referer, destination)

            if new_destination != destination:
                # We mark that we generated this redirection, so we don't modify it again
                self.redirected = True
                return redirect(new_destination)

        course_match = re.match(IN_COURSE_WIKI_REGEX, destination)
        if course_match:
            course_id = course_match.group('course_id')
            prepend_string = '/courses/' + course_match.group('course_id')
            wiki_reverse._transform_url = lambda url: prepend_string + url

        return None


    def process_response(self, request, response):
        """
        If this is a redirect response going to /wiki/*, then we might need
        to change it to be a redirect going to /courses/*/wiki*.
        """
        if not self.redirected and response.status_code == 302:   # This is a redirect
            referer = request.META.get('HTTP_REFERER')
            destination_url = response['LOCATION']
            destination = urlparse(destination_url).path

            new_destination = self.get_redirected_url(request.user, referer, destination)

            if new_destination != destination:
                new_url = destination_url.replace(destination, new_destination)
                response['LOCATION'] = new_url

        return response


    def get_redirected_url(self, user, referer, destination):
        """
        Returns None if the destination shouldn't be changed.
        """
        if not referer:
            return destination
        referer_path = urlparse(referer).path

        path_match = re.match(r'^/wiki/(?P<wiki_path>.*|)$', destination)
        if path_match:
            # We are going to the wiki. Check if we came from a course
            course_match = re.match(r'/courses/(?P<course_id>[^/]+/[^/]+/[^/]+)/.*', referer_path)
            if course_match:
                course_id = course_match.group('course_id')

                # See if we are able to view the course. If we are, redirect to it
                try:
                    course = get_course_with_access(user, course_id, 'load')
                    return "/courses/" + course.id + "/wiki/" + path_match.group('wiki_path')
                except Http404:
                    # Even though we came from the course, we can't see it. So don't worry about it.
                    pass

        else:
            # It is also possible we are going to a course wiki view, but we
            # don't have permission to see the course!
            course_match = re.match(IN_COURSE_WIKI_REGEX, destination)
            if course_match:
                course_id = course_match.group('course_id')
                # See if we are able to view the course. If we aren't, redirect to regular wiki
                try:
                    course = get_course_with_access(user, course_id, 'load')
                    # Good, we can see the course. Carry on
                    return destination
                except Http404:
                    # We can't see the course, so redirect to the regular wiki
                    return "/wiki/" + course_match.group('wiki_path')

        return destination


def context_processor(request):
    """
    This is a context processor which looks at the URL while we are
    in the wiki. If the url is in the form
    /courses/(course_id)/wiki/...
    then we add 'course' to the context. This allows the course nav
    bar to be shown.
    """

    match = re.match(IN_COURSE_WIKI_REGEX, request.path)
    if match:
        course_id = match.group('course_id')

        try:
            course = get_course_with_access(request.user, course_id, 'load')
            staff_access = has_access(request.user, course, 'staff')
            return {'course': course,
                    'staff_access': staff_access}
        except Http404:
            # We couldn't access the course for whatever reason. It is too late to change
            # the URL here, so we just leave the course context. The middleware shouldn't
            # let this happen
            pass

    return {}
