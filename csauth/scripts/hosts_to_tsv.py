
import csv
from collections import Counter
from logging import Logger

from common.file_wrapper import OutputFileWrapper


def main(logger: Logger, hosts_file: str):
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
            parts = line.strip('\n').split('\t')
            if len(parts) >= 3:
                print("parts", parts)
                writer.writerow(parts[:3])
                summary['outputted_lines'] += 1
            else:
                summary['skipped_lines'] += 1

    logger.info('\n* * * * Summary * * * *\n' + '\n'.join(f'{k}:  {summary[k]}' for k in summary))
    logger.debug("bye")
