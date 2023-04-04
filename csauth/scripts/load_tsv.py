
""" Load interchange formatted data into LDAP database.
    This script accepts 2x .tsv files as inputs.
    These 2x input files are generated by the unix_to_tsv script.
"""

import csv
from logging import Logger

from common import ldap_helpers

def main(
        logger: Logger,
        posix_user_tsv_path: str,
        posix_group_tsv_path: str
) -> None:
    logger.debug("load_tsv::main()")

    # # Read interchange formatted data from .tsv files into memory
    # logger.debug('reading ' + posix_user_tsv_path)
    # with open(posix_user_tsv_path) as f:
    #     user_tsv_rows = list(csv.reader(f, delimiter='\t'))
    # logger.debug('reading ' + posix_group_tsv_path)
    # with open(posix_group_tsv_path) as f:
    #     group_tsv_rows = list(csv.reader(f, delimiter='\t'))
    # logger.info(f"found {len(user_tsv_rows)} user rows to import")
    # logger.info(f"found {len(group_tsv_rows)} group rows to import")


    conn = ldap_helpers.new_connection()

    teststudent = ldap_helpers.posix_user_exists(conn, 'teststudent')
    print('teststudent', teststudent)

    student = ldap_helpers.posix_group_exists(conn, 'student')
    print('student', student)

    print("bye!")
    conn.unbind()
