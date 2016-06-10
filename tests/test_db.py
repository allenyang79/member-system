# -*- coding: utf-8 -*-
import os
import sys
import unittest

from app.config import config

class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_one(self):
        print config
        pass
        #db_path = os.path.join(os.path.dirname(__file__),'db/user.json')
        #user_db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))
        #user_db.insert({'type': 'apple', 'count': 7})
