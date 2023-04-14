
from collections import Counter
import csv
from logging import Logger

from common import ldap_helpers as ldap

def main(logger: Logger, hosts_tsv_file: str):
    summary = Counter()

    with open(hosts_tsv_file) as f:
        hosts_tsv_rows = list(csv.reader(f, delimiter='\t'))

    logger.info(f"found {len(hosts_tsv_rows)} host rows to import")

    with ldap.new_connection() as conn:

        for row in hosts_tsv_rows:
            (
                ipv4,
                _fqdn,
                alias,
            ) = row

            cn = alias
            if ldap.ip_host_exists(conn, cn):
                logger.debug(f'ipHost already exists in database {alias} {ipv4}')
                summary['skipping_host_already_added'] += 1
                continue

            ldap.add_ip_host(conn, cn, ipv4)





    logger.info('\n* * * * Summary * * * *\n' + '\n'.join(f'{k}:  {summary[k]}' for k in summary))
    logger.debug("bye")
