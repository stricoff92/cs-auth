

import sys

from common.script_logger import (
    get_debug_console_logger,
    get_task_logger
)
from scripts.patch_python_env import main as patch_python_env
from scripts.unix_to_tsv import main as unix_to_tsv


class COMMANDS:
    patch_python_env = 'patch_python_env'
    unix_to_tsv = 'unix_to_tsv'
    add_users = 'add_users'

if __name__ == '__main__':
    console = get_debug_console_logger()

    args = sys.argv[1:]
    console.info(f'csauth args: {args}')

    try:
        command = args[0]
    except IndexError:
        raise ValueError("script argument[0] (command) is required ")

    if command == COMMANDS.patch_python_env:
        patch_python_env(console)

    elif command == COMMANDS.unix_to_tsv:
        unix_to_tsv(console)

    elif command == COMMANDS.add_users:
        logger = get_task_logger('add-users')

    else:
        raise ValueError(f"unrecognized script argument[0] '{command}' (command name)")
