"""

LocalFile.py, LocalCanvasEntity class.
Represents a single file in the local file system.

"""

# Future imports
from __future__ import print_function

# Inbuilt modules
import json
import requests
import sys
import os

# Third party
from six import text_type

from CanvasSync import constants as CONSTANTS
from CanvasSync.local_entities.local_canvas_entity import LocalCanvasEntity
from CanvasSync.utilities import helpers
from CanvasSync.utilities.ANSI import ANSI


class LocalFile(LocalCanvasEntity):
    def __init__(self, file_info, file_history, parent):
        """
        Constructor method, initializes base LocalCanvasEntity class

        file_info     : dict   | A dictionary of information on the file object
        file_history  : dict   | A dictionary of information on the history of the local file object
        parent        : object | The parent object, a LocalModule object.
        """

        self.file_info = file_info
        file_name = file_info[u"name"]
        file_path = file_info[u"path"]

        # Initialize base class
        LocalCanvasEntity.__init__(self,
                                   name=file_name,
                                   sync_path=file_path,
                                   history=file_history,
                                   parent=parent,
                                   identifier=CONSTANTS.LOCAL_ET_FILE,
                                   entity_type=CONSTANTS.ENTITY_FILE)

    def __repr__(self):
        """ String representation, overwriting base class method """
        return "[{}] {}".format(CONSTANTS.LOCAL_ET_FILE, self.name)

    def upload_file(self, canvas_res):
        """
        Uploads this file to an appointed location provided by Canvas

        canvas_res : object | A dictionary of information on the file upload
        """
        file_upload_res = self.api.upload_file_to_url(
            canvas_res.get(CONSTANTS.FILE_UPLOAD_URL),
            canvas_res.get(CONSTANTS.FILE_UPLOAD_PARAMS),
            files=dict(
                file=(self.name, open(self.sync_path, 'rb'))
            )
        )
        file_upload_res.raise_for_status()
        file_upload_res_json = json.loads(file_upload_res.text)

        # When status code is 3XX, need to perform additional steps to complete upload
        # (https://canvas.instructure.com/doc/api/file.file_uploads.html#method.file_uploads.post)
        if 300 <= file_upload_res.status_code < 400:
            confirm_upload_res = requests.get(file_upload_res_json.get(CONSTANTS.FILE_UPLOAD_LOCATION),
                                              headers=self.api.get_auth_header())
            confirm_upload_res.raise_for_status()

        # Set this entity's ID
        self.id = file_upload_res_json.get(CONSTANTS.ID)
        modified_at = file_upload_res_json.get(CONSTANTS.HISTORY_MODIFIED_AT)
        timestamp = helpers.convert_utc_to_timestamp(modified_at)
        os.utime(self.sync_path, (timestamp, timestamp))

    def upload_to_canvas(self):
        """
        Uploads this file as a new file to Canvas
        """
        try:
            course = self.get_upper_level_entity(CONSTANTS.LOCAL_ET_COURSE)

            # TODO: Handle uploads to specific folder
            self.print_status(u"UPLOADING", color=u"blue", overwrite_previous_line=False)
            canvas_res = self.api.upload_file(course.id, dict(
                name=self.name,
                size=self.get_stat().st_size
            ))
            self.upload_file(canvas_res)
            self.print_status(u"UPLOADED", color=u"green", overwrite_previous_line=True)

            if self.parent.get_identifier_string() == CONSTANTS.LOCAL_ET_MODULE:
                module = self.parent
                self.print_status(u"ADDING TO MODULE", color=u"blue", overwrite_previous_line=False)
                self.api.upload_module_item(course.id, module.id, body=dict(
                    module_item=dict(
                        title=self.name,
                        type=CONSTANTS.MODULE_ITEM_TYPE_FILE,
                        content_id=self.id
                    )
                ))
                self.print_status(u"ADDED TO MODULE", color=u"green", overwrite_previous_line=True)

            self.get_synchronizer().update_history(self)
        except (IOError, requests.exceptions.HTTPError) as e:
            self.print_status(u"FAILED UPLOAD", color=u"red", message=u" {} ".format(e), overwrite_previous_line=True)

    def update_canvas_file(self):
        try:
            id = self.id
            file_info = self.api.get_file_by_id(id)
            folder_id = file_info.get(CONSTANTS.FILE_FOLDER_ID)
            self.print_status(u"UPDATING", color=u"blue", overwrite_previous_line=False)
            canvas_res = self.api.upload_file_by_folder(folder_id, dict(
                name=self.name,
                size=self.get_stat().st_size,
                on_duplicate='overwrite'
            ))
            self.upload_file(canvas_res)
            self.print_status(u"UPDATED", color=u"green", overwrite_previous_line=True)
            self.get_synchronizer().update_history(self)
        except (IOError, requests.exceptions.HTTPError) as e:
            self.print_status(u"FAILED UPDATE", color=u"red", message=u" {} ".format(e), overwrite_previous_line=True)

    def print_status(self, status, color, message='', overwrite_previous_line=False):
        """
        Print status to console
        """

        if overwrite_previous_line:
            # Move up one line
            sys.stdout.write(ANSI.format(u"", formatting=u"lineup"))
            sys.stdout.flush()

        print(ANSI.format(u"[%s] " % status, formatting=color) + str(self.name) + message)
        sys.stdout.flush()

    def walk(self):
        """
        Stop walking, endpoint
        """
        print(text_type(self))
        return

    def sync(self):
        """
        Synchronizes this file into Canvas
        """
        if self.history:
            history_modified_at = helpers.convert_utc_to_timestamp(self.get_history().get(CONSTANTS.HISTORY_MODIFIED_AT))
            local_file_modified_at = self.get_stat().st_mtime

            # A file is only updated if its modified time is later that the modified time tracked in the history
            if int(local_file_modified_at) > int(history_modified_at):
                self.update_canvas_file()
        else:
            self.upload_to_canvas()

    def show(self):
        """
        Show the folder hierarchy by printing every level
        """
        print(text_type(self))
