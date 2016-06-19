# -*- coding: utf-8 -*-
import os
import sys
import argparse


parser = argparse.ArgumentParser(
    description='custom config'
)

parser.add_argument(
    '--config', '-f',
    help='load custom config in configs',
    default='default'
)

parser.add_argument(
    '--debug',
    action='store_true',
    help='debug mode',
    default=False
)

def parse_args():
    """Parse args.
    you can mock this function when run unittest.
    """
    return parser.parse_args()

def load_config():
    # default
    args = parse_args()
    m = __import__('configs.default', fromlist=['default'])
    config.update(m.config)

    # by args.config
    m = __import__('configs.%s' % args.config, fromlist=[args.config])
    config.update(m.config)

config = {}
