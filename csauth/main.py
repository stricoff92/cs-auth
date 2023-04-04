
from logging import Logger
import sys

from common.script_logger import (
    get_debug_console_logger,
    get_task_logger
)
from common import security_helpers
from scripts.patch_python_env import main as patch_python_env
from scripts.unix_to_tsv import main as unix_to_tsv
from scripts.load_tsv import main as load_tsv


def bad_args_exit(console: Logger):
    console.error("Bad arguments")
    console.info("option: patch_python_env")
    console.info("option: unix_to_tsv <passwd_file> <shadow_file> <group_file>")
    console.info("option: load_tsv <posix_user_file> <posix_group_file>")
    console.info("option: add_users <bulk_import_tsv>")
    bad_args_exit_code = 128
    sys.exit(bad_args_exit_code)


# Available commands that this CLI app can execute
class COMMANDS:
    # Fix python 3.10 compat issues with ldap3 library
    patch_python_env = 'patch_python_env'

    # export unix users/groups to interchange formatted data
    unix_to_tsv = 'unix_to_tsv'

    # import interchange formatted data into LDAP database
    load_tsv = 'load_tsv'

    # covert a string to its base64 representation
    base_64_encode = 'base_64_encode'

    # Bulk import users/groups into LDAP database,
    # setup home directories,
    # create new account notices.
    add_users = 'add_users'


# Application entry point
if __name__ == '__main__':
    console = get_debug_console_logger()

    args = sys.argv[1:]
    console.debug(f'csauth args: {args}')

    try:
        command = args[0]
    except IndexError:
        bad_args_exit(console)

    # Test & Development scripts
    if command == COMMANDS.base_64_encode:
        try:
            value_to_encode = args[1]
        except IndexError:
            raise ValueError(
                "argument[1] is requried (value to encode)"
            )
        print(security_helpers.b64encode(value_to_encode))

    elif command == COMMANDS.patch_python_env:
        patch_python_env(console)

    elif command == COMMANDS.unix_to_tsv:
        try:
            passwd_file_name = args[1]
            shadow_file_name = args[2]
            group_file_name = args[3]
        except IndexError:
            raise ValueError(
                "argument[1], argument[2], argument[3] are requried (passwd, shadow, group file paths)"
            )
        unix_to_tsv(
            console,
            passwd_file_name,
            shadow_file_name,
            group_file_name,
        )

    elif command == COMMANDS.load_tsv:
        security_helpers.validate_applocals_file()
        try:
            posix_user_tsv_path = args[1]
            posix_group_tsv_path = args[2]
        except IndexError:
            raise ValueError(
                "argument[1], argument[2] are requried (posix_user_tsv_path, posix_group_tsv_path)"
            )
        logger = get_task_logger('load-tsv')
        load_tsv(logger, posix_user_tsv_path, posix_group_tsv_path)

    # Day to day management scripts
    elif command == COMMANDS.add_users:
        security_helpers.validate_applocals_file()
        logger = get_task_logger('add-users')

    else:
        console.error(f"Bad argument 0: {command}")
        bad_args_exit(console)
