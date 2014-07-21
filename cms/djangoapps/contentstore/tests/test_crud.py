import unittest
from xmodule import templates
from xmodule.modulestore.tests import persistent_factories
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore
from xmodule.seq_module import SequenceDescriptor
from xmodule.capa_module import CapaDescriptor
from xmodule.modulestore.locator import CourseLocator, BlockUsageLocator
from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.html_module import HtmlDescriptor
from xmodule.modulestore import inheritance
from xmodule.x_module import XModuleDescriptor


class TemplateTests(unittest.TestCase):
    """
    Test finding and using the templates (boilerplates) for xblocks.
    """

    def test_get_templates(self):
        found = templates.all_templates()
        self.assertIsNotNone(found.get('course'))
        self.assertIsNotNone(found.get('about'))
        self.assertIsNotNone(found.get('html'))
        self.assertIsNotNone(found.get('problem'))
        self.assertEqual(len(found.get('course')), 0)
        self.assertEqual(len(found.get('about')), 1)
        self.assertGreaterEqual(len(found.get('html')), 2)
        self.assertGreaterEqual(len(found.get('problem')), 10)
        dropdown = None
        for template in found['problem']:
            self.assertIn('metadata', template)
            self.assertIn('display_name', template['metadata'])
            if template['metadata']['display_name'] == 'Dropdown':
                dropdown = template
                break
        self.assertIsNotNone(dropdown)
        self.assertIn('markdown', dropdown['metadata'])
        self.assertIn('data', dropdown)
        self.assertRegexpMatches(dropdown['metadata']['markdown'], r'^Dropdown.*')
        self.assertRegexpMatches(dropdown['data'], r'<problem>\s*<p>Dropdown.*')

    def test_get_some_templates(self):
        self.assertEqual(len(SequenceDescriptor.templates()), 0)
        self.assertGreater(len(HtmlDescriptor.templates()), 0)
        self.assertIsNone(SequenceDescriptor.get_template('doesntexist.yaml'))
        self.assertIsNone(HtmlDescriptor.get_template('doesntexist.yaml'))
        self.assertIsNotNone(HtmlDescriptor.get_template('announcement.yaml'))

    def test_factories(self):
        test_course = persistent_factories.PersistentCourseFactory.create(org='testx', prettyid='tempcourse',
            display_name='fun test course', user_id='testbot')
        self.assertIsInstance(test_course, CourseDescriptor)
        self.assertEqual(test_course.display_name, 'fun test course')
        index_info = modulestore('split').get_course_index_info(test_course.location)
        self.assertEqual(index_info['org'], 'testx')
        self.assertEqual(index_info['prettyid'], 'tempcourse')

        test_chapter = persistent_factories.ItemFactory.create(display_name='chapter 1',
            parent_location=test_course.location)
        self.assertIsInstance(test_chapter, SequenceDescriptor)
        # refetch parent which should now point to child
        test_course = modulestore('split').get_course(test_chapter.location)
        self.assertIn(test_chapter.location.usage_id, test_course.children)

    def test_temporary_xblocks(self):
        """
        Test using load_from_json to create non persisted xblocks
        """
        test_course = persistent_factories.PersistentCourseFactory.create(org='testx', prettyid='tempcourse',
            display_name='fun test course', user_id='testbot')

        test_chapter = self.load_from_json({'category': 'chapter',
            'fields': {'display_name': 'chapter n'}},
            test_course.system, parent_xblock=test_course)
        self.assertIsInstance(test_chapter, SequenceDescriptor)
        self.assertEqual(test_chapter.display_name, 'chapter n')
        self.assertIn(test_chapter, test_course.get_children())

        # test w/ a definition (e.g., a problem)
        test_def_content = '<problem>boo</problem>'
        test_problem = self.load_from_json({'category': 'problem',
            'fields': {'data': test_def_content}},
            test_course.system, parent_xblock=test_chapter)
        self.assertIsInstance(test_problem, CapaDescriptor)
        self.assertEqual(test_problem.data, test_def_content)
        self.assertIn(test_problem, test_chapter.get_children())
        test_problem.display_name = 'test problem'
        self.assertEqual(test_problem.display_name, 'test problem')

    def test_persist_dag(self):
        """
        try saving temporary xblocks
        """
        test_course = persistent_factories.PersistentCourseFactory.create(org='testx', prettyid='tempcourse',
            display_name='fun test course', user_id='testbot')
        test_chapter = self.load_from_json({'category': 'chapter',
            'fields': {'display_name': 'chapter n'}},
            test_course.system, parent_xblock=test_course)
        test_def_content = '<problem>boo</problem>'
        # create child
        _ = self.load_from_json({'category': 'problem',
            'fields': {'data': test_def_content}},
            test_course.system, parent_xblock=test_chapter)
        # better to pass in persisted parent over the subdag so
        # subdag gets the parent pointer (otherwise 2 ops, persist dag, update parent children,
        # persist parent
        persisted_course = modulestore('split').persist_xblock_dag(test_course, 'testbot')
        self.assertEqual(len(persisted_course.children), 1)
        persisted_chapter = persisted_course.get_children()[0]
        self.assertEqual(persisted_chapter.category, 'chapter')
        self.assertEqual(persisted_chapter.display_name, 'chapter n')
        self.assertEqual(len(persisted_chapter.children), 1)
        persisted_problem = persisted_chapter.get_children()[0]
        self.assertEqual(persisted_problem.category, 'problem')
        self.assertEqual(persisted_problem.data, test_def_content)

    def test_delete_course(self):
        test_course = persistent_factories.PersistentCourseFactory.create(
            org='testx',
            prettyid='edu.harvard.history.doomed',
            display_name='doomed test course',
            user_id='testbot')
        persistent_factories.ItemFactory.create(display_name='chapter 1',
            parent_location=test_course.location)

        id_locator = CourseLocator(course_id=test_course.location.course_id, branch='draft')
        guid_locator = CourseLocator(version_guid=test_course.location.version_guid)
        # verify it can be retireved by id
        self.assertIsInstance(modulestore('split').get_course(id_locator), CourseDescriptor)
        # and by guid
        self.assertIsInstance(modulestore('split').get_course(guid_locator), CourseDescriptor)
        modulestore('split').delete_course(id_locator.course_id)
        # test can no longer retrieve by id
        self.assertRaises(ItemNotFoundError, modulestore('split').get_course, id_locator)
        # but can by guid
        self.assertIsInstance(modulestore('split').get_course(guid_locator), CourseDescriptor)

    def test_block_generations(self):
        """
        Test get_block_generations
        """
        test_course = persistent_factories.PersistentCourseFactory.create(
            org='testx',
            prettyid='edu.harvard.history.hist101',
            display_name='history test course',
            user_id='testbot')
        chapter = persistent_factories.ItemFactory.create(display_name='chapter 1',
            parent_location=test_course.location, user_id='testbot')
        sub = persistent_factories.ItemFactory.create(display_name='subsection 1',
            parent_location=chapter.location, user_id='testbot', category='vertical')
        first_problem = persistent_factories.ItemFactory.create(
            display_name='problem 1', parent_location=sub.location, user_id='testbot', category='problem',
            data="<problem></problem>"
        )
        first_problem.max_attempts = 3
        first_problem.save()  # decache the above into the kvs
        updated_problem = modulestore('split').update_item(first_problem, 'testbot')
        self.assertIsNotNone(updated_problem.previous_version)
        self.assertEqual(updated_problem.previous_version, first_problem.update_version)
        self.assertNotEqual(updated_problem.update_version, first_problem.update_version)
        updated_loc = modulestore('split').delete_item(updated_problem.location, 'testbot', delete_children=True)

        second_problem = persistent_factories.ItemFactory.create(
            display_name='problem 2',
            parent_location=BlockUsageLocator(updated_loc, usage_id=sub.location.usage_id),
            user_id='testbot', category='problem',
            data="<problem></problem>"
        )

        # course root only updated 2x
        version_history = modulestore('split').get_block_generations(test_course.location)
        self.assertEqual(version_history.locator.version_guid, test_course.location.version_guid)
        self.assertEqual(len(version_history.children), 1)
        self.assertEqual(version_history.children[0].children, [])
        self.assertEqual(version_history.children[0].locator.version_guid, chapter.location.version_guid)

        # sub changed on add, add problem, delete problem, add problem in strict linear seq
        version_history = modulestore('split').get_block_generations(sub.location)
        self.assertEqual(len(version_history.children), 1)
        self.assertEqual(len(version_history.children[0].children), 1)
        self.assertEqual(len(version_history.children[0].children[0].children), 1)
        self.assertEqual(len(version_history.children[0].children[0].children[0].children), 0)

        # first and second problem may show as same usage_id; so, need to ensure their histories are right
        version_history = modulestore('split').get_block_generations(updated_problem.location)
        self.assertEqual(version_history.locator.version_guid, first_problem.location.version_guid)
        self.assertEqual(len(version_history.children), 1)  # updated max_attempts
        self.assertEqual(len(version_history.children[0].children), 0)

        version_history = modulestore('split').get_block_generations(second_problem.location)
        self.assertNotEqual(version_history.locator.version_guid, first_problem.location.version_guid)

    # ================================= JSON PARSING ===========================
    # These are example methods for creating xmodules in memory w/o persisting them.
    # They were in x_module but since xblock is not planning to support them but will
    # allow apps to use this type of thing, I put it here.
    @staticmethod
    def load_from_json(json_data, system, default_class=None, parent_xblock=None):
        """
        This method instantiates the correct subclass of XModuleDescriptor based
        on the contents of json_data. It does not persist it and can create one which
        has no usage id.

        parent_xblock is used to compute inherited metadata as well as to append the new xblock.

        json_data:
        - 'location' : must have this field
        - 'category': the xmodule category (required or location must be a Location)
        - 'metadata': a dict of locally set metadata (not inherited)
        - 'children': a list of children's usage_ids w/in this course
        - 'definition':
        - '_id' (optional): the usage_id of this. Will generate one if not given one.
        """
        class_ = XModuleDescriptor.load_class(
            json_data.get('category', json_data.get('location', {}).get('category')),
            default_class
        )
        usage_id = json_data.get('_id', None)
        if not '_inherited_settings' in json_data and parent_xblock is not None:
            json_data['_inherited_settings'] = parent_xblock.xblock_kvs.get_inherited_settings().copy()
            json_fields = json_data.get('fields', {})
            for field in inheritance.INHERITABLE_METADATA:
                if field in json_fields:
                    json_data['_inherited_settings'][field] = json_fields[field]

        new_block = system.xblock_from_json(class_, usage_id, json_data)
        if parent_xblock is not None:
            children = parent_xblock.children
            children.append(new_block)
            # trigger setter method by using top level field access
            parent_xblock.children = children
            # decache pending children field settings (Note, truly persisting at this point would break b/c
            # persistence assumes children is a list of ids not actual xblocks)
            parent_xblock.save()
        return new_block

