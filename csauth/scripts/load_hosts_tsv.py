
import csv
from logging import Logger


def main(logger: Logger, hosts_tsv_file: str):

    with open(hosts_tsv_file) as f:
        hosts_tsv_rows = list(csv.reader(f, delimiter='\t'))

    logger.info(f"found {len(hosts_tsv_rows)} host rows to import")
