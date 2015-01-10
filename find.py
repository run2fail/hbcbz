#!/usr/bin/env python3

'''
Searches (zip/cbz) files for large for large files and duplicates.
'''

import argparse
import collections
import logging
import os
import zipfile


def parse():
    parser = argparse.ArgumentParser(description='Sanitize CBZ files')
    parser.add_argument(
        '--verbose', '-v',
        const=True, default=False, action='store_const',
        help='Show more output')
    parser.add_argument(
        '--tmp', '-t',
        type=str, default='/tmp',
        help='Root path for temporary directories (default=/tmp)')
    parser.add_argument(
        '--size', '-z',
        type=float, default=1.5,
        help='Size limit [MB] for candidates (candidates must be larger)')
    parser.add_argument(
        'files',
        nargs='*', default=[],
        help='Space separated list of CBZ files')
    args_dict = vars(parser.parse_args())
    return args_dict

def main():
    logging.basicConfig(format='%(asctime)s, %(levelname)8s: %(message)s', level=logging.INFO)
    args = parse()
    if args['verbose']:
        logging.root.setLevel(logging.DEBUG)
    for cbz in args['files']:
        if not os.path.isfile(cbz):
            continue
        logging.debug('Checking file: %s', cbz)
        try:
            with zipfile.ZipFile(cbz, 'r') as cbzzip:
                sizes = [round(zinfo.file_size/10**6, 1) for zinfo in cbzzip.filelist if zinfo.file_size > args['size']*10**6]
                duplicates = [zinfo.filename for zinfo in cbzzip.filelist]
                duplicates = [name for name, count in collections.Counter(duplicates).items() if count > 1]
                if len(sizes):
                    logging.info('Large files in: %s %s', cbz, sorted(sizes)[::-1])
                if len(duplicates):
                    logging.info('Duplicate files in: %s %s', cbz, duplicates)
        except zipfile.BadZipFile:
            logging.warning('Not a valid zip file: %s', cbz)

if __name__ == '__main__':
    main()
