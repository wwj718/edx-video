import fs.osfs
import os, os.path

from capa.capa_problem import LoncapaProblem
from mock import Mock, MagicMock

import xml.sax.saxutils as saxutils

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def tst_render_template(template, context):
    """
    A test version of render to template.  Renders to the repr of the context, completely ignoring
    the template name.  To make the output valid xml, quotes the content, and wraps it in a <div>
    """
    return '<div>{0}</div>'.format(saxutils.escape(repr(context)))

def calledback_url(dispatch = 'score_update'):
    return dispatch

xqueue_interface = MagicMock()
xqueue_interface.send_to_queue.return_value = (0, 'Success!')

def test_system():
    """
    Construct a mock ModuleSystem instance.

    """
    the_system = Mock(
        ajax_url='courses/course_id/modx/a_location',
        track_function=Mock(),
        get_module=Mock(),
        render_template=tst_render_template,
        replace_urls=Mock(),
        user=Mock(),
        filestore=fs.osfs.OSFS(os.path.join(TEST_DIR, "test_files")),
        debug=True,
        xqueue={'interface': xqueue_interface, 'construct_callback': calledback_url, 'default_queuename': 'testqueue', 'waittime': 10},
        node_path=os.environ.get("NODE_PATH", "/usr/local/lib/node_modules"),
        anonymous_student_id='student',
        cache=None,
        can_execute_unsafe_code=lambda: False,
    )
    return the_system

def new_loncapa_problem(xml, system=None):
    """Construct a `LoncapaProblem` suitable for unit tests."""
    return LoncapaProblem(xml, id='1', seed=723, system=system or test_system())
