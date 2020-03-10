"""

LocalCanvasEntity.py, Base class

The LocalCanvasEntity class is a module very similar to CanvasEntity, except that it represents the CanvasEntity from the
point of view of the local file system.

"""

# Inbuilt modules
import os

# CanvasSync module imports
from CanvasSync import constants as CONSTANTS
from CanvasSync.utilities import helpers


class LocalCanvasEntity(object):
    def __init__(self, name, sync_path, history=None, parent=None, api=None, settings=None, identifier="", entity_type="",
                 synchronizer=None):
        """
        Constructor method

        name         : string  | The name of the entity, e.g. this could be the name of a Course
        sync_path    : string  | A string representing the path to where the entity is synced from/to in the local folder
        history      : object  | An object representing the historical data of the entity in the local folder
        parent       : object  | An object representing the 'parent' to this LocalCanvasEntity, that is the LocalCanvasEntity one
                                 level above.
                                 Note that this does not mean parent in regards to inheritance.
        api          : object  | A CanvasSync InstructureApi object, should be the same object across the hierarchy during
                                 synchronization.
        settings     : object  | A CanvasSync Settings object, should be the same object across the hierarchy during
                                 synchronization.
        identifier   : string  | A string representing what derived class inherited from this instance of LocalCanvasEntity
        entity_type  : string  | A string representing what class of CanvasEntity this represents
        synchronizer : object  | The CanvasSync LocalSynchronizer object
        """

        self.history = history if history is not None else {}

        # Identifier information
        self.id = self.history.get(CONSTANTS.HISTORY_ID)

        # Parent object
        self.parent = parent

        # Identifier, could be "local_course", "local_module" ...
        self.identifier = identifier

        # Entity type, could be "course", "module" ...
        self.entity_type = entity_type

        # CanvasEntity name
        self.name = name

        # The same InstructureApi object is used across all Entities and so only the top-level Synchronizer object
        # is initialized with the object. All other lower level Entities fetches the object from their parent.
        if api:
            self.api = api
        else:
            self.api = self.get_parent().get_api()

        # Set settings object
        if settings:
            self.settings = settings
        else:
            self.settings = self.get_parent().get_settings()

        # Sync path
        if self.parent:
            parent_path = parent.get_path()
        else:
            parent_path = False

        is_folder = os.path.isdir(sync_path)

        # Get the path of the CanvasEntity in the local folder
        self.sync_path = helpers.get_corrected_path(sync_path, parent_path, folder=is_folder)

        # Child objects, that is Entities that are located below this current level in the folder hierarchy
        # E.g. this list could contain Item objects located under a Module object.
        self.children = []

        # Indent level
        if self.parent:
            self.indent = self.get_parent().indent + 1
        else:
            self.indent = -1

        # Set synchronizer object
        if synchronizer:
            self.synchronizer = synchronizer
        else:
            self.synchronizer = self.get_parent().get_synchronizer()

    def __getitem__(self, item):
        """ Container get-item method can be used to access a specific child object """
        return self.children[item]

    def __iter__(self):
        """ Iterator method yields all Entities contained by this CanvasEntity """
        for child in self.children:
            yield child

    def __repr__(self):
        """ String representation, overwritten in derived class """
        return u"Base object: %s" % self.name

    def __len__(self):
        """ len() method """
        return len(self.children)

    def __nonzero__(self):
        """ Boolean representation method. Always returns True after initialization. """
        return True

    def __bool__(self):
        """ Boolean representation method. Always returns True after initialization. """
        return self.__nonzero__()

    def get_identifier_string(self):
        """ Getter method for the identifier string """
        return self.identifier

    def get_entity_type(self):
        """ Getter method for the entity_type """
        return self.entity_type

    def get_upper_level_entity(self, entity_type):
        """
        Returns the LocalCanvasEntity of the specified entity type which is at a level of parent or higher than this entity.

        entity_type: string | A string representing a local entity type (e.g. local_course, local_file)
        """
        if self.get_identifier_string() == entity_type:
            return self

        parent = self.parent

        while parent is not None and parent.get_identifier_string() != entity_type :
            parent = parent.get_parent()

        return parent

    def get_name(self):
        """ Getter method for the name """
        return self.name

    def get_synchronizer(self):
        """ Getter method for the Synchronizer object """
        return self.synchronizer

    def get_history(self):
        """ Getter method for the history """
        return self.history

    def get_parent(self):
        """ Getter method for the parent object """
        return self.parent

    def get_api(self):
        """ Getter method for the InstructureApi object """
        return self.api

    def get_settings(self):
        """ Getter method for the Settings object """
        return self.settings

    def get_path(self):
        """ Getter method for the sync path """
        return self.sync_path

    def add_child(self, child):
        """ Add a child object to the list of children """
        self.children.append(child)

    def get_children(self):
        """ Getter method for the list of children """
        return self.children

    def get_stat(self):
        """ Getter method for the file attributes of this entity """
        return os.stat(self.sync_path)
