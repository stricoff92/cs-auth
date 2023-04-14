
from collections import Counter
import csv
from logging import Logger
import re

from common.file_wrapper import OutputFileWrapper


def main(logger: Logger, hosts_file: str):
    ipv4_patt = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    summary = Counter()

    host_lines = []
    with open(hosts_file) as f:
        for line in f:
            host_lines.append(line)
            summary['inputted_lines'] += 1

    hosts_output = OutputFileWrapper('etc-hosts', 'tsv')
    with hosts_output as f:
        writer = csv.writer(f, delimiter='\t')
        for line in host_lines:
            parts = [p for p in line.strip('\n').split('\t') if p.strip() != '']
            if len(parts) >= 3 and ipv4_patt.match(parts[0]):
                logger.debug(f'writing to output: {parts[:3]}')
                writer.writerow(parts[:3])
                summary['outputted_lines'] += 1
            else:
                summary['skipped_lines'] += 1

    logger.info('\n* * * * Summary * * * *\n' + '\n'.join(f'{k}:  {summary[k]}' for k in summary))
    logger.debug("bye")
