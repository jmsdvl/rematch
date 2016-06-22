#! /usr/bin/env python

"""
cli interface to the regex matching engine
"""

from argparse import ArgumentParser
import logging
import sys

from .regex import Regex


def get_args():
    parser = ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('pattern')
    parser.add_argument('strings', nargs='+')
    return parser.parse_args()


def cli():
    args = get_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    pattern = args.pattern
    try:
        match = Regex(pattern)
        strlen = max(len(string) for string in args.strings)
        out_fmt = '{:>' + str(strlen) + '}: {}'
        for string in args.strings:
            print(out_fmt.format(string, match(string)))
    except Exception as err:
        print('Error...')
        logging.debug('%s: %s %s' % sys.exc_info())
