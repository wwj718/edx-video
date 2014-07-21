import logging
import random

from xmodule.x_module import XModule
from xmodule.seq_module import SequenceDescriptor

from lxml import etree

from xblock.core import Scope, Integer

log = logging.getLogger('mitx.' + __name__)


class RandomizeFields(object):
    choice = Integer(help="Which random child was chosen", scope=Scope.user_state)


class RandomizeModule(RandomizeFields, XModule):
    """
    Chooses a random child module.  Chooses the same one every time for each student.

     Example:
     <randomize>
     <problem url_name="problem1" />
     <problem url_name="problem2" />
     <problem url_name="problem3" />
     </randomize>

    User notes:

      - If you're randomizing amongst graded modules, each of them MUST be worth the same
        number of points.  Otherwise, the earth will be overrun by monsters from the
        deeps.  You have been warned.

    Technical notes:
      - There is more dark magic in this code than I'd like.  The whole varying-children +
        grading interaction is a tangle between super and subclasses of descriptors and
        modules.
"""
    def __init__(self, *args, **kwargs):
        XModule.__init__(self, *args, **kwargs)

        # NOTE: calling self.get_children() creates a circular reference--
        # it calls get_child_descriptors() internally, but that doesn't work until
        # we've picked a choice
        num_choices = len(self.descriptor.get_children())

        if self.choice > num_choices:
            # Oops.  Children changed. Reset.
            self.choice = None

        if self.choice is None:
            # choose one based on the system seed, or randomly if that's not available
            if num_choices > 0:
                if self.system.seed is not None:
                    self.choice = self.system.seed % num_choices
                else:
                    self.choice = random.randrange(0, num_choices)

        if self.choice is not None:
            self.child_descriptor = self.descriptor.get_children()[self.choice]
            # Now get_children() should return a list with one element
            log.debug("children of randomize module (should be only 1): %s",
                      self.get_children())
            self.child = self.get_children()[0]
        else:
            self.child_descriptor = None
            self.child = None

    def get_child_descriptors(self):
        """
        For grading--return just the chosen child.
        """
        if self.child_descriptor is None:
            return []

        return [self.child_descriptor]


    def get_html(self):
        if self.child is None:
            # raise error instead?  In fact, could complain on descriptor load...
            return "<div>Nothing to randomize between</div>"

        return self.child.get_html()

    def get_icon_class(self):
        return self.child.get_icon_class() if self.child else 'other'


class RandomizeDescriptor(RandomizeFields, SequenceDescriptor):
    # the editing interface can be the same as for sequences -- just a container
    module_class = RandomizeModule

    filename_extension = "xml"


    def definition_to_xml(self, resource_fs):

        xml_object = etree.Element('randomize')
        for child in self.get_children():
            xml_object.append(
                etree.fromstring(child.export_to_xml(resource_fs)))
        return xml_object

    def has_dynamic_children(self):
        """
        Grading needs to know that only one of the children is actually "real".  This
        makes it use module.get_child_descriptors().
        """
        return True
