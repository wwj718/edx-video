from django.core.management.base import BaseCommand, CommandError
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.xml_importer import check_module_metadata_editability
from xmodule.course_module import CourseDescriptor

from request_cache.middleware import RequestCache

from django.core.cache import get_cache

CACHE = get_cache('mongo_metadata_inheritance')

class Command(BaseCommand):
    help = '''Enumerates through the course and find common errors'''

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("check_course requires one argument: <location>")

        loc_str = args[0]

        loc = CourseDescriptor.id_to_location(loc_str)
        store = modulestore()

        # setup a request cache so we don't throttle the DB with all the metadata inheritance requests
        store.set_modulestore_configuration({
            'metadata_inheritance_cache_subsystem': CACHE,
            'request_cache': RequestCache.get_request_cache()
        })

        course = store.get_item(loc, depth=3)

        err_cnt = 0

        def _xlint_metadata(module):
            err_cnt = check_module_metadata_editability(module)
            for child in module.get_children():
                err_cnt = err_cnt + _xlint_metadata(child)
            return err_cnt

        err_cnt = err_cnt + _xlint_metadata(course)

        # we've had a bug where the xml_attributes field can we rewritten as a string rather than a dict
        def _check_xml_attributes_field(module):
            err_cnt = 0
            if hasattr(module, 'xml_attributes') and isinstance(module.xml_attributes, basestring):
                print 'module = {0} has xml_attributes as a string. It should be a dict'.format(module.location.url())
                err_cnt = err_cnt + 1
            for child in module.get_children():
                err_cnt = err_cnt + _check_xml_attributes_field(child)
            return err_cnt

        err_cnt = err_cnt + _check_xml_attributes_field(course)

        # check for dangling discussion items, this can cause errors in the forums
        def _get_discussion_items(module):
            discussion_items = []
            if module.location.category == 'discussion':
                discussion_items = discussion_items + [module.location.url()]

            for child in module.get_children():
                discussion_items = discussion_items + _get_discussion_items(child)

            return discussion_items

        discussion_items = _get_discussion_items(course)

        # now query all discussion items via get_items() and compare with the tree-traversal
        queried_discussion_items = store.get_items(['i4x', course.location.org, course.location.course,
                                                    'discussion', None, None])

        for item in queried_discussion_items:
            if item.location.url() not in discussion_items:
                print 'Found dangling discussion module = {0}'.format(item.location.url())

