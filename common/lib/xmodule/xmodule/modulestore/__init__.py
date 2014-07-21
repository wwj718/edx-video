"""
This module provides an abstraction for working with XModuleDescriptors
that are stored in a database an accessible using their Location as an identifier
"""

import logging
import re

from collections import namedtuple

from .exceptions import InvalidLocationError, InsufficientSpecificationError
from xmodule.errortracker import make_error_tracker
from bson.son import SON

log = logging.getLogger('mitx.' + 'modulestore')

MONGO_MODULESTORE_TYPE = 'mongo'
XML_MODULESTORE_TYPE = 'xml'

URL_RE = re.compile("""
    (?P<tag>[^:]+)://?
    (?P<org>[^/]+)/
    (?P<course>[^/]+)/
    (?P<category>[^/]+)/
    (?P<name>[^@]+)
    (@(?P<revision>[^/]+))?
    """, re.VERBOSE)

# TODO (cpennington): We should decide whether we want to expand the
# list of valid characters in a location
INVALID_CHARS = re.compile(r"[^\w.-]")
# Names are allowed to have colons.
INVALID_CHARS_NAME = re.compile(r"[^\w.:-]")

# html ids can contain word chars and dashes
INVALID_HTML_CHARS = re.compile(r"[^\w-]")

_LocationBase = namedtuple('LocationBase', 'tag org course category name revision')


class Location(_LocationBase):
    '''
    Encodes a location.

    Locations representations of URLs of the
    form {tag}://{org}/{course}/{category}/{name}[@{revision}]

    However, they can also be represented as dictionaries (specifying each component),
    tuples or lists (specified in order), or as strings of the url
    '''
    __slots__ = ()

    @staticmethod
    def _clean(value, invalid):
        """
        invalid should be a compiled regexp of chars to replace with '_'
        """
        return re.sub('_+', '_', invalid.sub('_', value))

    @staticmethod
    def clean(value):
        """
        Return value, made into a form legal for locations
        """
        return Location._clean(value, INVALID_CHARS)

    @staticmethod
    def clean_keeping_underscores(value):
        """
        Return value, replacing INVALID_CHARS, but not collapsing multiple '_' chars.
        This for cleaning asset names, as the YouTube ID's may have underscores in them, and we need the
        transcript asset name to match. In the future we may want to change the behavior of _clean.
        """
        return INVALID_CHARS.sub('_', value)

    @staticmethod
    def clean_for_url_name(value):
        """
        Convert value into a format valid for location names (allows colons).
        """
        return Location._clean(value, INVALID_CHARS_NAME)

    @staticmethod
    def clean_for_html(value):
        """
        Convert a string into a form that's safe for use in html ids, classes, urls, etc.
        Replaces all INVALID_HTML_CHARS with '_', collapses multiple '_' chars
        """
        return Location._clean(value, INVALID_HTML_CHARS)

    @staticmethod
    def is_valid(value):
        '''
        Check if the value is a valid location, in any acceptable format.
        '''
        try:
            Location(value)
        except InvalidLocationError:
            return False
        return True

    @staticmethod
    def ensure_fully_specified(location):
        '''Make sure location is valid, and fully specified.  Raises
        InvalidLocationError or InsufficientSpecificationError if not.

        returns a Location object corresponding to location.
        '''
        loc = Location(location)
        for key, val in loc.dict().iteritems():
            if key != 'revision' and val is None:
                raise InsufficientSpecificationError(location)
        return loc

    def __new__(_cls, loc_or_tag=None, org=None, course=None, category=None,
                name=None, revision=None):
        """
        Create a new location that is a clone of the specifed one.

        location - Can be any of the following types:
            string: should be of the form
                    {tag}://{org}/{course}/{category}/{name}[@{revision}]

            list: should be of the form [tag, org, course, category, name, revision]

            dict: should be of the form {
                'tag': tag,
                'org': org,
                'course': course,
                'category': category,
                'name': name,
                'revision': revision,
            }
            Location: another Location object

        In both the dict and list forms, the revision is optional, and can be
        ommitted.

        Components must be composed of alphanumeric characters, or the
        characters '_', '-', and '.'.  The name component is additionally allowed to have ':',
        which is interpreted specially for xml storage.

        Components may be set to None, which may be interpreted in some contexts
        to mean wildcard selection.
        """

        if (org is None and course is None and category is None and name is None and revision is None):
            location = loc_or_tag
        else:
            location = (loc_or_tag, org, course, category, name, revision)

        if location is None:
            return _LocationBase.__new__(_cls, *([None] * 6))

        def check_dict(dict_):
            # Order matters, so flatten out into a list
            keys = ['tag', 'org', 'course', 'category', 'name', 'revision']
            list_ = [dict_[k] for k in keys]
            check_list(list_)

        def check_list(list_):
            def check(val, regexp):
                if val is not None and regexp.search(val) is not None:
                    log.debug('invalid characters val="%s", list_="%s"' % (val, list_))
                    raise InvalidLocationError("Invalid characters in '%s'." % (val))

            list_ = list(list_)
            for val in list_[:4] + [list_[5]]:
                check(val, INVALID_CHARS)
            # names allow colons
            check(list_[4], INVALID_CHARS_NAME)

        if isinstance(location, basestring):
            match = URL_RE.match(location)
            if match is None:
                log.debug('location is instance of %s but no URL match' % basestring)
                raise InvalidLocationError(location)
            groups = match.groupdict()
            check_dict(groups)
            return _LocationBase.__new__(_cls, **groups)
        elif isinstance(location, (list, tuple)):
            if len(location) not in (5, 6):
                log.debug('location has wrong length')
                raise InvalidLocationError(location)

            if len(location) == 5:
                args = tuple(location) + (None,)
            else:
                args = tuple(location)

            check_list(args)
            return _LocationBase.__new__(_cls, *args)
        elif isinstance(location, dict):
            kwargs = dict(location)
            kwargs.setdefault('revision', None)

            check_dict(kwargs)
            return _LocationBase.__new__(_cls, **kwargs)
        elif isinstance(location, Location):
            return _LocationBase.__new__(_cls, location)
        else:
            raise InvalidLocationError(location)

    def url(self):
        """
        Return a string containing the URL for this location
        """
        url = "{tag}://{org}/{course}/{category}/{name}".format(**self.dict())
        if self.revision:
            url += "@" + self.revision
        return url

    def html_id(self):
        """
        Return a string with a version of the location that is safe for use in
        html id attributes
        """
        s = "-".join(str(v) for v in self.list()
                     if v is not None)
        return Location.clean_for_html(s)

    def dict(self):
        """
        Return an OrderedDict of this locations keys and values. The order is
        tag, org, course, category, name, revision
        """
        return self._asdict()

    def list(self):
        return list(self)

    def __str__(self):
        return self.url()

    def __repr__(self):
        return "Location%s" % repr(tuple(self))

    @property
    def course_id(self):
        """
        Return the ID of the Course that this item belongs to by looking
        at the location URL hierachy.

        Throws an InvalidLocationError is this location does not represent a course.
        """
        if self.category != 'course':
            raise InvalidLocationError('Cannot call course_id for {0} because it is not of category course'.format(self))

        return "/".join([self.org, self.course, self.name])

    def replace(self, **kwargs):
        '''
        Expose a public method for replacing location elements
        '''
        return self._replace(**kwargs)


class ModuleStore(object):
    """
    An abstract interface for a database backend that stores XModuleDescriptor
    instances
    """
    def has_item(self, course_id, location):
        """
        Returns True if location exists in this ModuleStore.
        """
        raise NotImplementedError

    def get_item(self, location, depth=0):
        """
        Returns an XModuleDescriptor instance for the item at location.

        If any segment of the location is None except revision, raises
            xmodule.modulestore.exceptions.InsufficientSpecificationError

        If no object is found at that location, raises
            xmodule.modulestore.exceptions.ItemNotFoundError

        location: Something that can be passed to Location

        depth (int): An argument that some module stores may use to prefetch
            descendents of the queried modules for more efficient results later
            in the request. The depth is counted in the number of calls to
            get_children() to cache. None indicates to cache all descendents
        """
        raise NotImplementedError

    def get_instance(self, course_id, location, depth=0):
        """
        Get an instance of this location, with policy for course_id applied.
        TODO (vshnayder): this may want to live outside the modulestore eventually
        """
        raise NotImplementedError

    def get_item_errors(self, location):
        """
        Return a list of (msg, exception-or-None) errors that the modulestore
        encountered when loading the item at location.

        location : something that can be passed to Location

        Raises the same exceptions as get_item if the location isn't found or
        isn't fully specified.
        """
        raise NotImplementedError

    def get_items(self, location, course_id=None, depth=0):
        """
        Returns a list of XModuleDescriptor instances for the items
        that match location. Any element of location that is None is treated
        as a wildcard that matches any value

        location: Something that can be passed to Location

        depth: An argument that some module stores may use to prefetch
            descendents of the queried modules for more efficient results later
            in the request. The depth is counted in the number of calls to
            get_children() to cache. None indicates to cache all descendents
        """
        raise NotImplementedError

    def update_item(self, location, data, allow_not_found=False):
        """
        Set the data in the item specified by the location to
        data

        location: Something that can be passed to Location
        data: A nested dictionary of problem data
        """
        raise NotImplementedError

    def update_children(self, location, children):
        """
        Set the children for the item specified by the location to
        children

        location: Something that can be passed to Location
        children: A list of child item identifiers
        """
        raise NotImplementedError

    def update_metadata(self, location, metadata):
        """
        Set the metadata for the item specified by the location to
        metadata

        location: Something that can be passed to Location
        metadata: A nested dictionary of module metadata
        """
        raise NotImplementedError

    def delete_item(self, location):
        """
        Delete an item from this modulestore

        location: Something that can be passed to Location
        """
        raise NotImplementedError

    def get_courses(self):
        '''
        Returns a list containing the top level XModuleDescriptors of the courses
        in this modulestore.
        '''
        course_filter = Location("i4x", category="course")
        return self.get_items(course_filter)

    def get_course(self, course_id):
        '''
        Look for a specific course id.  Returns the course descriptor, or None if not found.
        '''
        raise NotImplementedError

    def get_parent_locations(self, location, course_id):
        '''Find all locations that are the parents of this location in this
        course.  Needed for path_to_location().

        returns an iterable of things that can be passed to Location.
        '''
        raise NotImplementedError

    def get_errored_courses(self):
        """
        Return a dictionary of course_dir -> [(msg, exception_str)], for each
        course_dir where course loading failed.
        """
        raise NotImplementedError

    def set_modulestore_configuration(self, config_dict):
        '''
        Allows for runtime configuration of the modulestore. In particular this is how the
        application (LMS/CMS) can pass down Django related configuration information, e.g. caches, etc.
        '''
        raise NotImplementedError

    def get_modulestore_type(self, course_id):
        """
        Returns a type which identifies which modulestore is servicing the given
        course_id. The return can be either "xml" (for XML based courses) or "mongo" for MongoDB backed courses
        """
        raise NotImplementedError


class ModuleStoreBase(ModuleStore):
    '''
    Implement interface functionality that can be shared.
    '''
    def __init__(self):
        '''
        Set up the error-tracking logic.
        '''
        self._location_errors = {}  # location -> ErrorLog
        self.modulestore_configuration = {}
        self.modulestore_update_signal = None  # can be set by runtime to route notifications of datastore changes

    def _get_errorlog(self, location):
        """
        If we already have an errorlog for this location, return it.  Otherwise,
        create one.
        """
        location = Location(location)
        if location not in self._location_errors:
            self._location_errors[location] = make_error_tracker()
        return self._location_errors[location]

    def get_item_errors(self, location):
        """
        Return list of errors for this location, if any.  Raise the same
        errors as get_item if location isn't present.

        NOTE: For now, the only items that track errors are CourseDescriptors in
        the xml datastore.  This will return an empty list for all other items
        and datastores.
        """
        # check that item is present and raise the promised exceptions if needed
        # TODO (vshnayder): post-launch, make errors properties of items
        # self.get_item(location)

        errorlog = self._get_errorlog(location)
        return errorlog.errors

    def get_errored_courses(self):
        """
        Returns an empty dict.

        It is up to subclasses to extend this method if the concept
        of errored courses makes sense for their implementation.
        """
        return {}

    def get_course(self, course_id):
        """Default impl--linear search through course list"""
        for c in self.get_courses():
            if c.id == course_id:
                return c
        return None

    @property
    def metadata_inheritance_cache_subsystem(self):
        """
        Exposes an accessor to the runtime configuration for the metadata inheritance cache
        """
        return self.modulestore_configuration.get('metadata_inheritance_cache_subsystem', None)

    @property
    def request_cache(self):
        """
        Exposes an accessor to the runtime configuration for the request cache
        """
        return self.modulestore_configuration.get('request_cache', None)

    def set_modulestore_configuration(self, config_dict):
        """
        This is the base implementation of the interface, all we need to do is store
        two possible configurations as attributes on the class
        """
        self.modulestore_configuration = config_dict


def namedtuple_to_son(namedtuple, prefix=''):
    """
    Converts a namedtuple into a SON object with the same key order
    """
    son = SON()
    for idx, field_name in enumerate(namedtuple._fields):
        son[prefix + field_name] = namedtuple[idx]
    return son
