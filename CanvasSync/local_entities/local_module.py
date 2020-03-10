"""

LocalModule.py, LocalCanvasEntity class.
Represents the module folder in the local file system.

"""

# Future imports
from __future__ import print_function

# Inbuilt modules
import os

# Third party
from six import text_type

# CanvasSync modules
from CanvasSync import constants as CONSTANTS
from CanvasSync.local_entities.local_canvas_entity import LocalCanvasEntity
from CanvasSync.local_entities.local_file import LocalFile
from CanvasSync.utilities import helpers


class LocalModule(LocalCanvasEntity):
    def __init__(self, module_info, module_history, module_position, parent):
        """, i
        Constructor method, initializes base CanvasEntity class and adds all children Folder and/or Item objects to the
        list of children

        module_info     : dict   | A dictionary of information on the local module object
        module_history  : dict   | A dictionary of information on the history of the local module object
        module_position : int    | An integer representing the position of the module in the folder (1 for first folder)
        parent          : object | The parent object, a LocalCourse object
        """

        self.module_info = module_info
        module_name = module_info[u"name"]  # TODO: Remove position prefix from modules
        module_path = module_info[u"path"]

        # Initialize base class
        LocalCanvasEntity.__init__(self,
                                   name=module_name,
                                   sync_path=module_path,
                                   history=module_history,
                                   parent=parent,
                                   identifier=CONSTANTS.LOCAL_ET_MODULE,
                                   entity_type=CONSTANTS.ENTITY_MODULE)

    def __repr__(self):
        """ String representation, overwriting base class method """
        return "[{}] {}".format(CONSTANTS.LOCAL_ET_MODULE, self.name)

    def add_items(self):
        """
        Method that adds all files listed under this module folder in the local file system to the list of children
        """

        # TODO: Handle folders for uploading entities such as Pages and Subheaders
        file_names, folder_names = helpers.get_files_and_folders(self.sync_path, include_full_path=False)

        for file_name in file_names:
            file_path = os.path.join(self.sync_path, file_name)
            file_info = dict(
                path=file_path,
                name=file_name
            )
            file_history = self.synchronizer.get_history_for_path(file_path)

            file = LocalFile(file_info, file_history, self)
            self.add_child(file)

    def walk(self):
        """
        Adds all LocalFile objects to the list of children and traverse them
        """
        print(text_type(self))

        self.add_items()

        for item in self:
            item.walk()

    def sync(self):
        """
        Adds all LocalFile objects to the list of children and synchronize them
        """
        print(text_type(self))

        self.add_items()

        for child in self:
            child.sync()

    def show(self):
        """
        Show the folder hierarchy by printing every level
        """
        print(text_type(self))

        for child in self:
            child.show()
