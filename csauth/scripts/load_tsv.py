
from logging import Logger


def main(
        logger: Logger,
        posix_user_tsv_path: str,
        posix_group_tsv_path: str
):
    logger.info("load_tsv::main()")

