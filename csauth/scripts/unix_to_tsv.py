
"""
Consolidate unix passwd, shadow, and group
    files into an interchange format (2x .tsv files)

    .tsv USER  file: holds info for PosixUser type  (passwd + shadow data)

        tsv columns: user-name uid guid hashed-password user-details home-directory login-shell

    .tsv GROUP file: holds info for PoxixGroup type (passwd + group data)

        tsv columns: group-name, group-uid, member-uids

    These 2 files holding interchange formatted data
    can be imported into OpenLDAP using 'object_load' script.
"""
import csv
from logging import Logger

from common.command_runner import CommandRunner
from common.file_wrapper import OutputFileWrapper
from common.unix_indexes import (
    ShadowLineIXs,
    PasswdLineIXs,
    GroupLineIXs,
)


GROUPS_TO_SKIP = frozenset([
    'mail',
    'wheel',
    'audio',
    'pkcs11',
])

def _build_output(
    logger: Logger,
    posix_user_output: OutputFileWrapper,
    posix_group_output: OutputFileWrapper,
    passwd_text: str,
    shadow_text: str,
    group_text: str,
):

    # create map of {username => shadow data, ....}
    username_shadow_map = {}

    for shadow_line in shadow_text.split("\n"):
        shadow_line_parts = shadow_line.split(":")
        if len(shadow_line_parts) != 9:
            continue
        if not shadow_line_parts[ShadowLineIXs.HASHED_PASSWORD].startswith("$"):
            continue
        if shadow_line_parts[ShadowLineIXs.USER_NAME] in username_shadow_map:
            logger.warning("found duplicate shadow entry")
            continue
        username_shadow_map[shadow_line_parts[ShadowLineIXs.USER_NAME]] = shadow_line_parts

    # create a map of {username -> uid}
    username_to_uids_map = {}

    # Process passwd/shadow data into rows of PosixUsers
    with posix_user_output as fp:

        user_writer = csv.writer(fp, delimiter='\t')

        for passwd_line in passwd_text.split("\n"):
            passwd_line_parts = passwd_line.split(":")
            if len(passwd_line_parts) != 7:
                logger.warning(
                    f"skipping passwd line. Unexpected number of line parts: {passwd_line_parts}"
                )
                continue

            if passwd_line_parts[PasswdLineIXs.PLAINTEXT_PASSWORD] != 'x':
                logger.warning(
                    f"skipping passwd line. Unexpected plaintext password found"
                )
                continue

            if int(passwd_line_parts[PasswdLineIXs.USER_UID]) < 1000:
                continue

            shadow_parts = username_shadow_map.get(passwd_line_parts[PasswdLineIXs.USER_NAME])
            if shadow_parts is None:
                logger.warning(
                    f"skipping passwd line. could not find corresponding shadow entry"
                )
                continue

            user_writer.writerow([
                passwd_line_parts[PasswdLineIXs.USER_NAME],
                passwd_line_parts[PasswdLineIXs.USER_UID],
                passwd_line_parts[PasswdLineIXs.USER_GROUP_GUID],
                shadow_parts[ShadowLineIXs.HASHED_PASSWORD],
                passwd_line_parts[PasswdLineIXs.USER_DETAILS],
                passwd_line_parts[PasswdLineIXs.HOME_DIRECTORY],
                passwd_line_parts[PasswdLineIXs.LOGIN_SHELL],
            ])

    # Process passwd/group data into rows of PosixGroups
    with posix_group_output as fp:
        group_writer = csv.writer(fp, delimiter='\t')

        for group_line in group_text.split("\n"):
            group_line_parts = group_line.split(":")
            if len(group_line_parts) != 4:
                logger.warning(
                    f"skipping group line. has incorrect number of parts: {group_line_parts}"
                )
                continue

            if group_line_parts[GroupLineIXs.GROUP_NAME] in GROUPS_TO_SKIP:
                continue

            if not group_line_parts[GroupLineIXs.GROUP_MEMBERS].strip():
                # Group has no members
                continue

            #tsv columns: group-name, group-uid, member-uids
            group_writer.writerow([
                group_line_parts[GroupLineIXs.GROUP_NAME],
                group_line_parts[GroupLineIXs.GROUP_GUID],
                group_line_parts[GroupLineIXs.GROUP_MEMBERS],
            ])

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

    posix_user_output = OutputFileWrapper('posixUser', 'tsv')
    posix_group_output = OutputFileWrapper('posixGroup', 'tsv')
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
