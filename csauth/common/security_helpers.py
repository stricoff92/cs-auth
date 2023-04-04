
""" Misc. security related functions
"""

import base64
import os.path
import stat

from settings import BASE_DIR


def b64encode(val: str) -> str:
    return base64.b64encode(val.encode()).decode()

def b64decode(val: str) -> str:
    return base64.b64decode(val.encode()).decode()


class ApplocalsError(Exception):
    pass

class ApplocalsFileNotFoundError(ApplocalsError):
    pass

class ApplocalsFileInvalidConfigurationError(ApplocalsError):
    pass

def validate_applocals_file() -> None:
    locals_file_path = os.path.join(BASE_DIR, 'applocals.py')

    # check file exists
    if not os.path.exists(locals_file_path):
        raise ApplocalsFileNotFoundError()

    # check file has correct permissions
    st = os.stat(locals_file_path)
    owner_can_read = bool(st.st_mode & stat.S_IRUSR)
    owner_can_write = bool(st.st_mode & stat.S_IWUSR)
    group_can_read = bool(st.st_mode & stat.S_IRGRP)
    group_can_write = bool(st.st_mode & stat.S_IWGRP)
    public_can_read = bool(st.st_mode & stat.S_IROTH)
    public_can_write = bool(st.st_mode & stat.S_IWOTH)

    # Check owner can read write
    if not owner_can_read or not owner_can_write:
        raise ApplocalsFileInvalidConfigurationError(
            'applocals.py has incorrect permissions. OWNER CANNOT READ/WRTIE. '
            + 'Run command "chmod 600 applocals.py"'
        )

    # Check group has no access
    if group_can_read or group_can_write:
        raise ApplocalsFileInvalidConfigurationError(
            'applocals.py has incorrect permissions. GROUP CAN READ/WRTIE. '
            + 'Run command "chmod 600 applocals.py"'
        )

    # Check public has no access
    if public_can_read or public_can_write:
        raise ApplocalsFileInvalidConfigurationError(
            'applocals.py has incorrect permissions. PUBLIC CAN READ/WRTIE. '
            + 'Run command "chmod 600 applocals.py"'
        )
