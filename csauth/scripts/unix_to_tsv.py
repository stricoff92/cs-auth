
from logging import Logger

from common.tmp_file_wrapper import OutputFileWrapper
from common.command_runner import CommandRunner

def main(logger: Logger):
    logger.info("unix_to_tsv::main()")
    output = OutputFileWrapper()

    cmd = CommandRunner('ls /etc')
    print(cmd.read_result())
