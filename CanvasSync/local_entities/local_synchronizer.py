"""

LocalSynchronizer.py, manages local resources for upload synchronization.

"""

# Future imports
from __future__ import print_function

# Inbuilt modules
import os

# CanvasSync modules
from CanvasSync.local_entities.local_course import LocalCourse
from CanvasSync.utilities import helpers
from CanvasSync.utilities.ANSI import ANSI
from CanvasSync.utilities.history import History


class LocalSynchronizer:
    def __init__(self, settings, api):
        """
        Constructor method, initializes all LocalCourse objects to start upload synchronnization.

        settings : object | A Settings object, has top-level sync path attribute
        api      : object | An InstructureApi object
        """

        if not settings.is_loaded():
            settings.load_settings("")

        # Start sync by clearing the console window
        helpers.clear_console()

        # Initialize reference to settings and api objects
        self.settings = settings
        self.api = api

        # A list of LocalCourses objects representing course folders in the local file system
        self.courses = []

        self.history = History(settings)

    def add_courses(self):
        """
        Method that adds all Course objects representing Canvas courses to the
        list of children
        """

        _, course_names = helpers.get_files_and_folders(self.settings.sync_path, include_full_path=False)

        for course_name in course_names:
            course_path = os.path.join(self.settings.sync_path, course_name)
            course_info = dict(
                path=course_path,
                name=course_name
            )
            course_history = self.history.get_history_for_path(course_path)

            course = LocalCourse(course_info, course_history, self, self.api, self.settings)
            self.courses.append(course)

    def update_history(self, entity):
        """
        Call this method when there is a new or updated entity in the local file system that is to be uploaded to Canvas.
        This will update the history file that tracks the local canvas entities.
        """
        self.history.write_entity_to_file(entity)

    def get_history_for_path(self, entity_path):
        """
        Returns the first row of record within the entity history file with a matching path to the specified path.

        entity_path : string | absolute path to local entity
        """
        return self.history.get_history_for_path(entity_path)

    def walk(self):
        """
        Adds all LocalCourse to the list of children and traverse them
        """

        # Print initial walk message
        print(ANSI.format(u"\n[*] Mapping out your local folder hierarchy. "
                          u"Please wait...", u"red"))
        self.add_courses()

        for course in self.courses:
            course.walk()

    def sync(self):
        """
        Adds all LocalCourse objects to the list of children and synchronize them
        """
        print(u"\n[*] Synchronizing from folder: %s\n" % self.settings.sync_path)

        self.add_courses()
        for course in self.courses:
            course.sync()
