
from logging import Logger

from common.tmp_file_wrapper import OutputFileWrapper
from common.command_runner import CommandRunner

# YP files
PASSWD_FILE = '/var/yp/passwd'
SHADOW_FILE = '/var/yp/shadow'
GROUP_FILE = '/etc/group'

# Regular UNIX files
# PASSWD_FILE = '/etc/passwd'
# SHADOW_FILE = '/etc/shadow'
# GROUP_FILE = '/etc/group'

def _build_output(
    output: OutputFileWrapper,
    cat_passwd_cmd,
    cat_shadow_cmd,
    cat_group_cmd
):
    pass

def main(logger: Logger):
    logger.info("unix_to_tsv::main()")
    output = OutputFileWrapper()
    cat_passwd_cmd = CommandRunner(f'cat {PASSWD_FILE}')
    cat_shadow_cmd = CommandRunner(f'cat {SHADOW_FILE}')
    cat_group_cmd = CommandRunner(f'cat {GROUP_FILE}')

    try:
        _build_output(
            output,
            cat_passwd_cmd,
            cat_shadow_cmd,
            cat_group_cmd,
        )
    except Exception:
        raise
    finally:
        logger.info("deleting cat output files...")
        cat_passwd_cmd.delete_results()
        cat_shadow_cmd.delete_results()
        cat_group_cmd.delete_results()