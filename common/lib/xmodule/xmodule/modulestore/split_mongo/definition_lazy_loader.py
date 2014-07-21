from xmodule.modulestore.locator import DescriptionLocator


class DefinitionLazyLoader(object):
    """
    A placeholder to put into an xblock in place of its definition which
    when accessed knows how to get its content. Only useful if the containing
    object doesn't force access during init but waits until client wants the
    definition. Only works if the modulestore is a split mongo store.
    """
    def __init__(self, modulestore, definition_id):
        """
        Simple placeholder for yet-to-be-fetched data
        :param modulestore: the pymongo db connection with the definitions
        :param definition_locator: the id of the record in the above to fetch
        """
        self.modulestore = modulestore
        self.definition_locator = DescriptionLocator(definition_id)

    def fetch(self):
        """
        Fetch the definition. Note, the caller should replace this lazy
        loader pointer with the result so as not to fetch more than once
        """
        return self.modulestore.definitions.find_one(
            {'_id': self.definition_locator.definition_id})
