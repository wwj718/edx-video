from xmodule.x_module import XModule
from xmodule.raw_module import RawDescriptor


class HiddenModule(XModule):
    def get_html(self):
        if self.system.user_is_staff:
            return "ERROR: This module is unknown--students will not see it at all"
        else:
            return ""


class HiddenDescriptor(RawDescriptor):
    module_class = HiddenModule
