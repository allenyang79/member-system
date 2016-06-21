# -*- coding: utf-8 -*-
import os
import sys
import argparse

config = {}

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


def _parse_args():
    """parse args from cli.

    You can mock this function for unittest.
    """
    args = parser.parse_args()

def load_config():
    global config
    if config:
        print 'pass load_config if loaded.'
        return

    args = _parse_args()
    print "load_config", args
    m = __import__('configs.default', fromlist=['default'])
    config.update(m.config)

    m = __import__('configs.%s' % args.config, fromlist=[args.config])
    config.update(m.config)



