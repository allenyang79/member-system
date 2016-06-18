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
    global box, db, client

    load_config(['--config', 'test', '--debug'])
    app.db.init_db()

    from mongobox import MongoBox
    box = MongoBox()
    box.start()

    client = box.client()  # pymongo client
    db = client[config['DB_NAME']]

    app.db._client = client
    app.db._db = db

def bye():
    global box
    if box and box :
        box.stop()

atexit.register(bye)
