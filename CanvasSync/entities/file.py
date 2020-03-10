"""
CanvasSync by Mathias Perslev
February 2017

--------------------------------------------

file, CanvasEntity Class

The File class stores information on files hosted on the Canvas server. It represents an end point in the hierarchy and
contains no child objects. When the sync method is invoked the file will be downloaded or skipped depending on if it is
already present in at the sync path.

A Module, SubHeader, Folder or Assignment object is the parent object.

See developer_info.txt file for more information on the class hierarchy of CanvasEntities objects.

"""

# Future imports
from __future__ import print_function

# Inbuilt modules
import os
import sys

# Third party
from six import text_type

from CanvasSync import constants as CONSTANTS
from CanvasSync.entities.canvas_entity import CanvasEntity
from CanvasSync.utilities import helpers
from CanvasSync.utilities.ANSI import ANSI

class File(CanvasEntity):
    def __init__(self, file_info, parent, add_to_list_of_entities=True):
        """
        Constructor method, initializes base CanvasEntity class

        assignment_info : dict   | A dictionary of information on the Canvas file object
        parent          : object | The parent object, a Module, SubHeader, Folder or Assignment object
        """

        self.file_info = file_info

        self.locked = self.file_info[CONSTANTS.FILE_LOCKED_FOR_USER]

        file_id = self.file_info[CONSTANTS.HISTORY_ID]
        file_name = helpers.get_corrected_name(self.file_info[CONSTANTS.DISPLAY_NAME])
        file_path = os.path.join(parent.get_path(), file_name)

        # Initialize base class
        CanvasEntity.__init__(self,
                              id_number=file_id,
                              name=file_name,
                              sync_path=file_path,
                              parent=parent,
                              folder=False,
                              identifier=CONSTANTS.ENTITY_FILE,
                              add_to_list_of_entities=add_to_list_of_entities)

    def __repr__(self):
        """ String representation, overwriting base class method """
        return u" " * 15 + u"|   " + u"\t" * self.indent + u"%s: %s" % (ANSI.format(u"File",
                                                                                    formatting=u"file"),
                                                                        self.name)

    def download(self):
        """ Download the file """
        if os.path.exists(self.sync_path):
            remote_file_modified_at = helpers.convert_utc_to_timestamp(self.file_info.get(CONSTANTS.HISTORY_MODIFIED_AT))
            local_file_modified_at = os.stat(self.sync_path).st_mtime
            if remote_file_modified_at == local_file_modified_at:
                return False

        self.print_status(u"DOWNLOADING", color=u"blue")

        # Download file payload from server
        file_data = self.api.download_file_payload(self.file_info[u"url"])

        # Write data to file
        try:
            with open(self.sync_path, u"wb") as out_file:
                out_file.write(file_data)

        except KeyboardInterrupt as e:
            # If interrupted mid-writing, delete the corrupted file
            if os.path.exists(self.sync_path):
                os.remove(self.sync_path)

            # Re-raise, will be catched in CanvasSync.py
            raise e

        modified_at = self.file_info.get(CONSTANTS.HISTORY_MODIFIED_AT)
        id = self.file_info.get(CONSTANTS.ID)
        path = self.sync_path

        # Update file access date and modified date
        timestamp = helpers.convert_utc_to_timestamp(modified_at)
        os.utime(self.sync_path, (timestamp, timestamp))

        # Update sync history
        history_record = dict({
            CONSTANTS.HISTORY_ID: id,
            CONSTANTS.HISTORY_MODIFIED_AT: modified_at,
            CONSTANTS.HISTORY_PATH: path,
            CONSTANTS.HISTORY_TYPE: CONSTANTS.ENTITY_FILE
        })
        self.synchronizer.history.write_history_record_to_file(history_record)

        return True

    def print_status(self, status, color, overwrite_previous_line=False):
        """ Print status to console """

        if overwrite_previous_line:
            # Move up one line
            sys.stdout.write(ANSI.format(u"", formatting=u"lineup"))
            sys.stdout.flush()

        print(ANSI.format(u"[%s]" % status, formatting=color) + str(self)[len(status) + 2:])
        sys.stdout.flush()

    def walk(self, counter):
        """ Stop walking, endpoint """
        print(text_type(self))

        counter[0] += 1
        return

    def sync(self):
        """
        Synchronize the file by downloading it from the Canvas server and saving it to the sync path
        If the file has already been downloaded, skip downloading.
        File objects have no children objects and represents an end point of a folder traverse.
        """
        if not self.locked:
            was_downloaded = self.download()
            self.print_status(u"SYNCED", color=u"green", overwrite_previous_line=was_downloaded)
        else:
            self.print_status(u"LOCKED", color=u"red", overwrite_previous_line=False)

    def show(self):
        """ Show the folder hierarchy by printing every level """
        print(text_type(self))
