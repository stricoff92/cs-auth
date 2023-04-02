
""" Wrapper for creating, reading, writing, and deleting
    temporary files to the disk.
"""
import os
import os.path
from typing import Tuple
import uuid


from settings import TMP_DIR

class TMPFileWrapper:

    def __init__(self):
        self.name, self.full_path = self._get_new_path()

    @property
    def read_args(self):
        return (self.full_path, 'r')

    @property
    def write_args(self):
        return (self.full_path, 'w')

    def _get_new_path(self) -> Tuple:
        while True:
            name = str(uuid.uuid4())
            full_path = os.path.join(TMP_DIR, name)
            if os.path.exists(full_path):
                continue
            self._touch(full_path)
            return name, full_path

    def remove(self):
        os.remove(self.full_path)

    def _touch(full_path: str) -> str:
        with open(full_path, 'w') as _:
            pass
