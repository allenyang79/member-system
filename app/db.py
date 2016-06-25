import os
import sys
import functools
import pymongo

from werkzeug.local import LocalProxy
from app.config import config


_db = None
_client = None

def _init_db():
    client = pymongo.MongoClient(config['DB_HOST'], config['DB_PORT'])
    db = client[config['DB_NAME']]
    return client, db


def find_db():
    global _client, _db
    if not _db:
        _client, _db = _init_db()
    return _db

db = LocalProxy(find_db)
