

import sys

from common.script_logger import get_debug_console_logger
from scripts.unix_to_tsv import main as unix_to_tsv
from settings import BASE_DIR


class COMMANDS:
    unix_to_tsv = 'unix_to_tsv'

if __name__ == '__main__':
    console = get_debug_console_logger()

    args = sys.argv[1:]
    console.info(f'csauth args: {args}')

    try:
        command = args[0]
    except IndexError:
        raise ValueError("script argument[0] (command) is required ")

    if command == COMMANDS.unix_to_tsv:
        unix_to_tsv(console)

    else:
        raise ValueError("unrecognized script argument[0] (command name)")
