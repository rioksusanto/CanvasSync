"""

LocalCourse.py, LocalCanvasEntity class.
Represents the course folder in the local file system.

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
from CanvasSync.local_entities.local_module import LocalModule
from CanvasSync.utilities import helpers

# Special folder names within a Course folder
NON_MODULE_FOLDER_NAMES = [CONSTANTS.FOLDER_ASSIGNMENTS, CONSTANTS.FOLDER_OTHERS]


class LocalCourse(LocalCanvasEntity):
    def __init__(self, course_info, course_history, synchronizer, api, settings):
        """
        Constructor method, initializes base LocalCanvasEntity class

        course_info     : dict     | A dictionary of information on the file object
        course_history  : dict     | A dictionary of information on the history of the local course object
        synchronizer    : object   | A LocalSynchronizer object
        api             : object   | An InstructureApi object
        settings        : object   | A Settings object
        """
        self.course_info = course_info
        course_path = course_info[u"path"]
        course_name = course_info[u"name"]

        self.to_be_synced = True if course_name in settings.courses_to_sync else False

        # Initialize base class
        LocalCanvasEntity.__init__(self,
                                   name=course_name,
                                   sync_path=course_path,
                                   history=course_history,
                                   api=api,
                                   settings=settings,
                                   identifier=CONSTANTS.LOCAL_ET_COURSE,
                                   entity_type=CONSTANTS.ENTITY_COURSE,
                                   synchronizer=synchronizer)

    def __repr__(self):
        """String representation, overwriting base class method """
        return "[{}] {}".format(CONSTANTS.LOCAL_ET_COURSE, self.name)

    def add_modules(self):
        """
        Method that adds all LocalModule objects to the list of children
        """

        _, folder_names = helpers.get_files_and_folders(self.sync_path, include_full_path=False)
        module_names = [f_name for f_name in folder_names if f_name not in NON_MODULE_FOLDER_NAMES]

        for idx, module_name in enumerate(module_names):
            module_path = os.path.join(self.sync_path, module_name)
            module_info = dict(
                path=module_path,
                name=module_name
            )
            module_history = self.synchronizer.get_history_for_path(module_path)

            # TODO: Get proper module position by parsing the number prefixed in module folder's name
            module = LocalModule(module_info, module_history, idx, self)
            self.add_child(module)

    def walk(self):
        """
        Adds all LocalModules objects to the list of children and traverse them
        """

        if not self.to_be_synced:
            return

        if not list(self.settings.modules_settings.values()) == [False, False, False]:
            self.add_modules()

        print(text_type(self))

        # TODO: Include "Other files" folder

        for child in self:
            child.walk()

    def sync(self):
        """
        Adds all LocalModules objects to the list of children and synchronize them
        """
        print(text_type(self))

        if not self.to_be_synced:
            return

        if not list(self.settings.modules_settings.values()) == [False, False, False]:
            self.add_modules()

        # TODO: Include "Other files" folder

        for child in self:
            child.sync()

    def show(self):
        """
        Show the folder hierarchy by printing every level
        """
        print(text_type(self))

        for child in self:
            child.show()
