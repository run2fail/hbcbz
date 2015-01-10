#!/usr/bin/env python3

'''
Sanitize CBZ files

Sanitize comic book archive files downloaded from Humble Bundle. This includes
removal of duplicate files and resizing of the contained images. Some CBZ files
in Humble Bundles contain JPEGs with a size of 10 MB and rarely more than 20 MB
(with about 16,000 px width).
This cannot be handled by systems with limited RAM - especially tablets or
mobile phone. In fact, even laptops with 4 GB RAM may struggle with such large
images.

Features:
- Resizes images
- Removes duplicates
- Removes non-image files
'''

import argparse
import logging
import os
import re
import sys
import tempfile
import zipfile

import PIL
from PIL import Image


def parse():
    def convert_resize(args_dict):
        regex = re.compile(r'(?P<max_x>\d+)?x(?P<max_y>\d+)?')
        match = regex.match(args_dict['resize'])
        if not match:
            logging.critical('Invalid resize parameter: %s', args_dict['resize'])
            sys.exit(1)
        try:
            args_dict['max_x'] = int(match.groupdict()['max_x'])
        except TypeError:
            args_dict['max_x'] = -1
        try:
            args_dict['max_y'] = int(match.groupdict()['max_y'])
        except TypeError:
            args_dict['max_y'] = -1

    parser = argparse.ArgumentParser(description='Sanitize CBZ files')
    parser.add_argument(
        '--verbose', '-v',
        const=True, default=False, action='store_const',
        help='Show more output')
    parser.add_argument(
        '--resize', '-r',
        type=str, default='1440x',
        help='Resize image keeping aspect ratio (default=1440x)')
    parser.add_argument(
        '--quality', '-q',
        type=int, default=75,
        help='Quality parameter for the image compression algorithm (default=75)')
    parser.add_argument(
        '--tmp', '-t',
        type=str, default='/tmp',
        help='Root path for temporary directories (default=/tmp)')
    parser.add_argument(
        'files',
        nargs='*', default=[],
        help='Space separated list of CBZ files')
    args_dict = vars(parser.parse_args())
    convert_resize(args_dict)
    return args_dict

class SecurityException(Exception):
    pass

def extract(cbz, tmpdir):
    logging.debug('Extracting file: %s', cbz)
    try:
        with zipfile.ZipFile(cbz, 'r') as cbzzip:
            for member in cbzzip.namelist():
                logging.debug('Extracting: %s/%s', tmpdir, member)
                if member.startswith('/') or member.startswith('..'):
                    raise SecurityException('Out of tmpdir write attempt: %s', member)
                if os.path.exists('%s/%s' % (tmpdir, member)):
                    logging.info('Skipping duplicate file: %s', member)
                    continue
                cbzzip.extract(member, path=tmpdir)
    except zipfile.BadZipFile:
        logging.error('Invalid CBZ zip file: %s', cbz)

def add_filename_suffix(fname, suffix):
    pre, ext = os.path.splitext(fname)
    return os.path.join(pre + '-' + suffix + ext)

def compress(cbz, tmpdir):
    cbz_old = add_filename_suffix(cbz, 'orig')
    os.rename(cbz, cbz_old)
    logging.debug('Compressing to file: %s', cbz)
    with zipfile.ZipFile(cbz, 'w', zipfile.ZIP_DEFLATED) as cbzzip:
        for root, dirs, files in os.walk(tmpdir):
            for fname in sorted(files):
                filepath = os.path.join(root, fname)
                logging.debug('Compressing: %s', filepath)
                arcname = os.path.relpath(filepath, tmpdir)
                cbzzip.write(filepath, arcname=arcname)

def resize(args, tmpdir):
    for fname in sorted(os.listdir(tmpdir)):
        filepath = os.path.join(tmpdir, fname)
        if os.path.isdir(filepath):
            resize(args, filepath)
            continue
        filepath_resized = add_filename_suffix(filepath, 'resized')
        try:
            img = Image.open(filepath)
        except OSError:
            logging.warning('Not a valid image: %s', filepath)
            continue
        if ((args['max_x'] <= 0 or img.size[0] <= args['max_x']) and
           (args['max_y'] <= 0 or img.size[1] <= args['max_y'])):
            logging.debug('Image is small enough: %s %s', filepath, img.size)
        else:
            logging.debug('Resizing image: %s %s', filepath, img.size)
            width = min([x for x in [args['max_x'], img.size[0]] if x > 0])
            height = min([y for y in [args['max_y'], img.size[1]] if y > 0])
            img.thumbnail((width, height), Image.ANTIALIAS)
        img.save(filepath_resized, format=img.format, quality=args['quality'])
        size_before = os.path.getsize(filepath)
        size_after = os.path.getsize(filepath_resized)
        if size_before <= size_after:
            os.remove(filepath_resized)
        else:
            os.rename(filepath_resized, filepath)

def main():
    logging.basicConfig(format='%(asctime)s, %(levelname)8s: %(message)s', level=logging.INFO)
    args = parse()
    if args['verbose']:
        logging.root.setLevel(logging.DEBUG)
    for cbz in args['files']:
        logging.info('Sanitizing file: %s', cbz)
        with tempfile.TemporaryDirectory(dir=args['tmp']) as tmpdir:
            if not os.path.isfile(cbz):
                logging.error('Cannot access file: %s', cbz)
                continue
            extract(cbz, tmpdir)
            resize(args, tmpdir)
            compress(cbz, tmpdir)

if __name__ == '__main__':
    main()
