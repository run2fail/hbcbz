#!/usr/bin/env python3

'''
Renames CBZ files. Removes the numeric suffix in the filename.

Example: foobar_1234.cbz -> foobar.cbz
'''

import argparse
import logging
import os
import re


def parse():
    parser = argparse.ArgumentParser(description='Rename CBZ files')
    parser.add_argument(
        '--verbose', '-v',
        const=True, default=False, action='store_const',
        help='Show more output')
    parser.add_argument(
        'files',
        nargs='*', default=[],
        help='Space separated list of CBZ files')
    args_dict = vars(parser.parse_args())
    return args_dict

def rename(cbz):
    if not cbz.endswith('.cbz'):
        logging.warning('Not a CBZ file: %s', cbz)
        return
    regex = re.compile(r'(.*)_\d+\.cbz')
    match = regex.match(cbz)
    if not match:
        logging.warning('Does not match: %s', cbz)
        return
    newname = match.group(1) + '.cbz'
    if os.path.exists(newname):
        logging.error('File with destination name exists: %s', newname)
        return
    logging.debug('Renaming: %s -> %s', cbz, newname)
    os.rename(cbz, newname)

def main():
    logging.basicConfig(format='%(asctime)s, %(levelname)8s: %(message)s', level=logging.INFO)
    args = parse()
    if args['verbose']:
        logging.root.setLevel(logging.DEBUG)
    for cbz in args['files']:
        logging.debug('Handling file: %s', cbz)
        rename(cbz)

if __name__ == '__main__':
    main()
