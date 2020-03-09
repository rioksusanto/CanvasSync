"""
History

Sync history state management.

"""

# Future imports
from __future__ import print_function

# Inbuilt modules
import os

# Third party modules
import csv

from CanvasSync.constants import HISTORY_ID
from CanvasSync.constants import HISTORY_PATH
from CanvasSync.constants import HISTORY_MODIFIED_AT
from CanvasSync.constants import HISTORY_TYPE

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

    def get_record_idx(self, record):
        try:
            return [idx for idx, row in enumerate(self.history) if row.get(HISTORY_PATH) == record.get(HISTORY_PATH) and row.get(HISTORY_TYPE) == record.get(HISTORY_TYPE)][0]
        except:
            return -1

    def write_history_record_to_file(self, data):
        fieldnames = [HISTORY_ID, HISTORY_PATH, HISTORY_MODIFIED_AT, HISTORY_TYPE]
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
