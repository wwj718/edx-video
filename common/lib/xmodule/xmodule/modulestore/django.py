"""
Module that provides a connection to the ModuleStore specified in the django settings.

Passes settings.MODULESTORE as kwargs to MongoModuleStore
"""

from __future__ import absolute_import
from importlib import import_module

from django.conf import settings
from xmodule.modulestore.loc_mapper_store import LocMapperStore

_MODULESTORES = {}

FUNCTION_KEYS = ['render_template']


def load_function(path):
    """
    Load a function by name.

    path is a string of the form "path.to.module.function"
    returns the imported python object `function` from `path.to.module`
    """
    module_path, _, name = path.rpartition('.')
    return getattr(import_module(module_path), name)


def create_modulestore_instance(engine, options):
    """
    This will return a new instance of a modulestore given an engine and options
    """
    class_ = load_function(engine)

    _options = {}
    _options.update(options)

    for key in FUNCTION_KEYS:
        if key in _options and isinstance(_options[key], basestring):
            _options[key] = load_function(_options[key])

    return class_(
        **_options
    )


def modulestore(name='default'):
    """
    This returns an instance of a modulestore of given name. This will wither return an existing
    modulestore or create a new one
    """
    if name not in _MODULESTORES:
        _MODULESTORES[name] = create_modulestore_instance(settings.MODULESTORE[name]['ENGINE'],
                                                          settings.MODULESTORE[name]['OPTIONS'])

    return _MODULESTORES[name]

_loc_singleton = None
def loc_mapper():
    """
    Get the loc mapper which bidirectionally maps Locations to Locators. Used like modulestore() as
    a singleton accessor.
    """
    # pylint: disable=W0603
    global _loc_singleton
    # pylint: disable=W0212
    if _loc_singleton is None:
        # instantiate
        _loc_singleton = LocMapperStore(settings.modulestore_options)
    return _loc_singleton

