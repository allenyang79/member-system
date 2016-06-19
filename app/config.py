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



def load_config(custom_args=None):
    global config
    if config:
        print "pass load_config if loaded."
        return

    if custom_args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(custom_args)

    m = __import__('configs.default', fromlist=['default'])
    config.update(m.config)

    # by args.config
    m = __import__('configs.%s' % args.config, fromlist=[args.config])
    config.update(m.config)

config = {}
