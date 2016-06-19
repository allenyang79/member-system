# -*- coding: utf-8 -*-
import os, sys
import atexit
import re

import unittest
import mock
from app.config import config, load_config
import app.db

box = None
db = None
client = None
def setup():
    print "===mock config==="
    from app.config import parser

    args = parser.parse_args(['--config', 'test', '--debug'])
    mock_parse_args = mock.patch('app.config.parse_args', return_value=args)
    mock_parse_args.start()

    print "===mock db==="
    from mongobox import MongoBox

    global box, db, client

    box = MongoBox()
    box.start()

    client = box.client()  # pymongo client
    db = client['test']
    #mock_parse_args = mock.patch('app.db.db', return_value=db)
    app.db._client = client
    app.db._db = db

    # ========================
    load_config()

def bye():
    global box
    if box and box :
        box.stop()

atexit.register(bye)
