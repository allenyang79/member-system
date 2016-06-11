import os
import sys
import pymongo

from werkzeug.local import LocalProxy
from app.config import config


def init():
    global _db
    if config['MODE'] == 'test':
        # run on test mode
        from mongobox import MongoBox
        box = MongoBox()
        box.start()
        client = box.client()  # pymongo client
        _db = client[config['DB_NAME']]
    else:
        client = MongoClient()
        _db = client[config['DB_NAME']]


def find_db():
    if _db is None:
        raise Exception('models has not init')
    else:
        return _db

_db = None
db = LocalProxy(find_db)
