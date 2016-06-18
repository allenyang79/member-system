import os
import sys
import functools
import pymongo

from werkzeug.local import LocalProxy
from app.config import config


def init_db():
    print "init db"
    global _client, _db
    _client = pymongo.MongoClient(config['DB_HOST'], config['DB_PORT'])
    _db = _client[config['DB_NAME']]


def find_db():
    global _db
    if _db:
        return _db
    else:
        raise Exception('please un app.db.init_db first')


_db = None
_client = None
db = LocalProxy(functools.partial(find_db))
