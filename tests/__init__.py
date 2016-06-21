# -*- coding: utf-8 -*-
import os, sys
import atexit
import re

import unittest
import mock

#import app.config as config
from app.config import parser, config
import app.server

box = None

def setup():
    print "custom config"
    def side_effect():
        return parser.parse_args(['--config', 'test', '--debug'])#from

    mock_load_config = mock.patch('app.config._parse_args', side_effect=side_effect)
    mock_load_config.start()

    print "custom db"
    from mongobox import MongoBox
    global box, db, client
    box = MongoBox()
    box.start()

    def side_effect():
        client = box.client()  # pymongo client
        db = client['test']
        return client, db

    mock_init_db = mock.patch('app.db._init_db', side_effect=side_effect)
    mock_init_db.start()



def bye():
    global box
    if box:
        box.stop()

atexit.register(bye)
