
"""
Consolidate unix passwd, shadow, and group
    files into an interchange format (2x .tsv files)

    .tsv USER  file: holds info for PosixUser type  (passwd + shadow data)
    .tsv GROUP file: holds info for PoxixGroup type (passwd + group data)

    These 2 files holding interchange formatted data
    can be imported into OpenLDAP using 'object_load' script.
"""


from logging import Logger

from common.file_wrapper import OutputFileWrapper
from common.command_runner import CommandRunner

class PasswdLineIXs:
    """ Indexes of data held in the unix style passwd file
        index 1 data should always be 'x' indicating the password is
            hashed and stored in shadow
    """
    USER_NAME = 0
    PLAINTEXT_PASSWORD = 1
    USER_UID = 2
    USER_GROUP_GUID = 3
    USER_DETAILS = 4
    HOME_DIRECTORY = 5
    LOGIN_SHELL = 6


def _build_output(
    logger: Logger,
    posix_user_output: OutputFileWrapper,
    posix_group_output: OutputFileWrapper,
    passwd_text: str,
    shadow_text: str,
    group_text: str,
):
    for passwd_line in passwd_text.split("\n"):
        passwd_line_parts = passwd_line.split(":")


def main(
    logger: Logger,
    passwd_file_name,
    shadow_file_name,
    group_file_name,
):
    logger.info("unix_to_tsv::main()")
    logger.info("passwd file " + passwd_file_name)
    logger.info("shadow file " + shadow_file_name)
    logger.info("group file " + group_file_name)

    posix_user_output = OutputFileWrapper()
    posix_group_output = OutputFileWrapper()
    cat_passwd_cmd = CommandRunner(f'cat {passwd_file_name}')
    cat_shadow_cmd = CommandRunner(f'cat {shadow_file_name}')
    cat_group_cmd = CommandRunner(f'cat {group_file_name}')

    try:
        _build_output(
            logger,
            posix_user_output,
            posix_group_output,
            cat_passwd_cmd.read_result(),
            cat_shadow_cmd.read_result(),
            cat_group_cmd.read_result(),
        )
    except Exception:
        raise
    finally:
        logger.info("deleting cat output files...")
        cat_passwd_cmd.delete_results()
        cat_shadow_cmd.delete_results()
        cat_group_cmd.delete_results()
