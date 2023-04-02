

import argparse

from scripts.unix_to_tsv import main as unix_to_tsv
from settings import BASE_DIR


if __name__ == '__main__':
    print(BASE_DIR)
    unix_to_tsv()


