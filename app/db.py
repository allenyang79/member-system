import os
import sys
import functools
import pymongo

from werkzeug.local import LocalProxy
from app.config import config


_db = None
_client = None

def _find_db():
    global _client, _db
    if not _db:
        print "==init db=="
        _client = pymongo.MongoClient(config['DB_HOST'], config['DB_PORT'])
        _db = _client[config['DB_NAME']]
    return _db

find_db = functools.partial(_find_db)  #mock this on unittest
db = LocalProxy(find_db)
