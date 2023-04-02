
from logging import Logger

from common.tmp_file_wrapper import OutputFileWrapper

def main(logger: Logger):
    logger.info("unix_to_tsv::main()")
    output = OutputFileWrapper()

