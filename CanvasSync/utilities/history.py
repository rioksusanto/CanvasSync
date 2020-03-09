"""
History

Sync history state management.

"""

# Future imports
from __future__ import print_function

# Inbuilt modules
import os
import calendar
from datetime import datetime

# Third party modules
import csv

from CanvasSync.utilities import helpers

class History:
    def __init__(self, settings):
        self.history_file_path = os.path.join(settings.sync_path, settings.history_file_name)
        self.history = self.get_history_from_file(self.history_file_path)

    def get_history_from_file(self, path):
        if os.path.exists(path):
            with open(path, newline='') as file:
                data = list(csv.DictReader(file))
                return data
        else:
            return []

    def get_record_idx(self, record):
        try:
            return [idx for idx, row in enumerate(self.history) if row.get('id') == record.get('id')][0]
        except:
            return -1

    def write_history_record_to_file(self, data):
        record_index = self.get_record_idx(data)
        if record_index != -1:
            self.history[record_index] = data
            with open(self.history_file_path, 'w', newline='') as file:
                fieldnames = ['id', 'path', 'modified_at']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.history)
        elif self.history == []:
            self.history.append(data)
            with open(self.history_file_path, 'w', newline='') as file:
                fieldnames = ['id', 'path', 'modified_at']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.history)
        else:
            self.history.append(data)
            with open(self.history_file_path, 'a', newline='') as file:
                fieldnames = ['id', 'path', 'modified_at']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writerow(data)
