"""
This configuration is to run the MixedModuleStore on a localdev environment
"""

# We intentionally define lots of variables that aren't used, and
# want to import all variables from base settings files
# pylint: disable=W0401, W0614

from .dev import *, DATA_DIR

MODULESTORE = {
    'default': {
        'ENGINE': 'xmodule.modulestore.mixed.MixedModuleStore',
        'OPTIONS': {
            'mappings': {
                'MITx/2.01x/2013_Spring': 'xml'
            },
            'stores': {
                'xml': {
                    'ENGINE': 'xmodule.modulestore.xml.XMLModuleStore',
                    'OPTIONS': {
                        'data_dir': DATA_DIR,
                        'default_class': 'xmodule.hidden_module.HiddenDescriptor',
                    }
                },
                'default': {
                    'ENGINE': 'xmodule.modulestore.mongo.MongoModuleStore',
                    'OPTIONS': {
                        'default_class': 'xmodule.raw_module.RawDescriptor',
                        'host': 'localhost',
                        'db': 'xmodule',
                        'collection': 'modulestore',
                        'fs_root': DATA_DIR,
                        'render_template': 'mitxmako.shortcuts.render_to_string',
                    }
                }
            },
        }
    }
}
