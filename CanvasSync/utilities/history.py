"""
History

Sync history state management.

"""

# Future imports
from __future__ import print_function

# Inbuilt modules
import logging
import os

# Third party modules
import csv

# CanvasSync modules
from CanvasSync import constants as CONSTANTS
from CanvasSync.local_entities.local_file import LocalFile
from CanvasSync.utilities import helpers


class History:
    def __init__(self, settings):
        self.history_file_path = os.path.join(settings.sync_path, settings.history_file_name)
        self.history = self.__get_history_from_file(self.history_file_path)

    @staticmethod
    def __get_history_from_file(path):
        if os.path.exists(path):
            with open(path, newline='') as file:
                data = list(csv.DictReader(file))
                return data
        else:
            return []

    def get_history_for_path(self, path):
        """
        Returns the first row of record within the entity history file with a matching path to the specified path.

        path : string | absolute path to local entity
        """
        try:
            return [row for idx, row in enumerate(self.history) if os.path.normpath(row.get('path')) == os.path.normpath(path)][0]
        except IndexError:
            return None

    def get_record_idx(self, record):
        try:
            return [idx for idx, row in enumerate(self.history)
                    if row.get(CONSTANTS.HISTORY_PATH) == record.get(CONSTANTS.HISTORY_PATH) and
                    row.get(CONSTANTS.HISTORY_TYPE) == record.get(CONSTANTS.HISTORY_TYPE)][0]
        except:
            return -1

    def write_history_record_to_file(self, data):
        fieldnames = [CONSTANTS.HISTORY_ID, CONSTANTS.HISTORY_PATH, CONSTANTS.HISTORY_MODIFIED_AT, CONSTANTS.HISTORY_TYPE]
        record_index = self.get_record_idx(data)
        if record_index != -1:
            self.history[record_index] = data
            with open(self.history_file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.history)
        elif not self.history:
            self.history.append(data)
            with open(self.history_file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.history)
        else:
            self.history.append(data)
            with open(self.history_file_path, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writerow(data)

    def write_entity_to_file(self, entity):
        """
        Keeps track of local file entities by updating their data on the entity history file.

        entity : object | A LocalFile object
        """

        if type(entity) is not LocalFile:
            logging.debug('Excluding update of entity {} from history.'.format(entity))
            return

        self.write_history_record_to_file(dict({
            CONSTANTS.HISTORY_ID: entity.id,
            CONSTANTS.HISTORY_MODIFIED_AT: helpers.convert_timestamp_to_utc(entity.get_stat().st_mtime),
            CONSTANTS.HISTORY_PATH: entity.sync_path,
            CONSTANTS.HISTORY_TYPE: entity.entity_type
        }))
