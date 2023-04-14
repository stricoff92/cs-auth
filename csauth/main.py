
import argparse
import getpass
import sys

from common.constants import (
    SKIP_FLAG
)
from common.script_logger import (
    get_console_logger,
    get_task_logger
)
from common import security_helpers


# Available commands that this CLI app can execute
class COMMANDS:
    # test connections to port 389 & 636 using python client
    test_python_client = 'test_python_client'

    # export unix users/groups to interchange formatted data
    unix_to_tsv = 'unix_to_tsv'

    # export /etc/hosts interchange formatted data
    hosts_to_tsv = 'hosts_to_tsv'

    # import interchange formatted data into LDAP database
    load_tsv = 'load_tsv'

    # covert a string to its base64 representation
    base_64_encode = 'base_64_encode'

    # Bulk import users/groups into LDAP database,
    # setup home directories,
    # create new account notices.
    add_users = 'add_users'

def new_base_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="CS-AUTH OpenLDAP Management Command Suite",
        description="Run Management Commands to Interact with OpenLDAP.",
    )
    parser.add_argument(
        'command_name', help="Management Command to Execute.")
    return parser


# Application entry point
if __name__ == '__main__':
    console = get_console_logger()

    console.debug("parsing args...")
    base_parser = new_base_arg_parser()
    base_args, _unknown_args = base_parser.parse_known_args()
    console.debug(f'base args {base_args}')

    # Test & Development scripts
    # TODO: Delete these commands.
    if base_args.command_name == COMMANDS.base_64_encode:
        value_to_encode = getpass.getpass("Enter a value to encode: ")
        print(security_helpers.b64encode(value_to_encode))

    elif base_args.command_name == COMMANDS.test_python_client:
        from scripts.test_python_client import main as test_python_client
        test_python_client(console)

    elif base_args.command_name == COMMANDS.unix_to_tsv:
        from scripts.unix_to_tsv import main as unix_to_tsv

        parser = new_base_arg_parser()
        parser.add_argument('passwd_file', help="The unix passwd file to import")
        parser.add_argument('shadow_file', help="The unix shadow file to import")
        parser.add_argument('group_file', help="The unix group file to import")
        cmd_args = parser.parse_args()
        console.debug(f'cmd args {cmd_args}')

        unix_to_tsv(
            console,
            cmd_args.passwd_file,
            cmd_args.shadow_file,
            cmd_args.group_file,
        )

    elif base_args.command_name == COMMANDS.hosts_to_tsv:
        from scripts.hosts_to_tsv import main as hosts_to_tsv

        parser = new_base_arg_parser()
        parser.add_argument('hosts_file', help="The unix passwd file to import")
        cmd_args = parser.parse_args()
        console.debug(f'cmd args {cmd_args}')
        hosts_to_tsv(console, cmd_args.hosts_file)

    elif base_args.command_name == COMMANDS.load_tsv:
        from scripts.load_tsv import main as load_tsv

        security_helpers.validate_applocals_file()
        parser = new_base_arg_parser()
        parser.add_argument('user_file', help="The user tsv file to import")
        parser.add_argument('group_file', help="The group tsv file to import")
        parser.add_argument(
            '--password', '-p',
            help="use a given user password instead of the imported passwords",
            action='store_true',
            default=False
        )
        parser.add_argument(
            '--skipusers', action='store_true', help='Don\'t import users', default=False)
        parser.add_argument(
            '--skipgroups', action='store_true', help='Don\'t import groups', default=False)
        cmd_args = parser.parse_args()
        console.debug(f'cmd args {cmd_args}')

        if cmd_args.password:
            console.debug("ignoring imported password, will use a new password for user(s)")
            given_password = getpass.getpass("new password for user(s): ")
        else:
            console.debug("using imported password(s)")
            given_password = None

        logger = get_task_logger('load-tsv')
        load_tsv(
            logger,
            SKIP_FLAG if cmd_args.skipusers else cmd_args.user_file,
            SKIP_FLAG if cmd_args.skipgroups else cmd_args.group_file,
            given_password=given_password,
        )

    # Day to day management scripts
    elif base_args.command_name == COMMANDS.add_users:
        security_helpers.validate_applocals_file()
        parser = new_base_arg_parser()
        parser.parse_args()
        logger = get_task_logger('add-users')

    else:
        console.error(f"Unknown command name: {base_args.command_name}")
        console.error("run ./main -h for help.")
        exit_code = 128
        sys.exit(exit_code)
