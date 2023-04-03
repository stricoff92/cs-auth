
""" Wrapper for creating, reading, writing, and deleting
    temporary files to the disk.
"""

from abc import abstractmethod
import datetime as dt
import os
import os.path
from typing import Tuple
import uuid

from settings import TMP_DIR, OUTPUTS_DIR


class BaseFileWrapper:

    OUT_DIR = NotImplemented

    def __init__(self):
        self._fp = None
        self.name, self.full_path = self._get_new_path()

    @property
    def read_args(self):
        return (self.full_path, 'r')

    @property
    def write_args(self):
        return (self.full_path, 'a')

    @abstractmethod
    def _get_new_name(self) -> str:
        ...

    def _get_new_path(self) -> Tuple:
        while True:
            name = self._get_new_name()
            full_path = os.path.join(self.OUT_DIR, name)
            if os.path.exists(full_path):
                continue
            self._touch(full_path)
            return name, full_path

    def remove(self):
        os.remove(self.full_path)

    def _touch(self, full_path: str) -> str:
        with open(full_path, 'w') as _:
            pass

    def __enter__(self):
        self._fp = open(*self.write_args)
        return self._fp

    def __exit__(self, *args):
        self._fp.close()

class TMPFileWrapper(BaseFileWrapper):
    OUT_DIR = TMP_DIR
    def _get_new_name(self):
        return str(uuid.uuid4())

class OutputFileWrapper(BaseFileWrapper):
    OUT_DIR = OUTPUTS_DIR

    def __init__(self, report_name: str, file_extension: str, *a, **k):
        self._report_name = report_name
        self._file_extension = file_extension
        super().__init__(*a, **k)


    def _get_new_name(self):
        return dt.datetime.now().strftime(
            '%Y-%m-%d_%H%M%S%f' + '_' + self._report_name + '.' + self._file_extension
        )
