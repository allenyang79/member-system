# -*- coding: utf-8 -*-
import os
import sys
import unittest

from app.config import config
from app.models import session, User


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create(self):
        u = User(name='allen', phone='0988')
        session.add(u)
        session.commit()
        pass
        #db_path = os.path.join(os.path.dirname(__file__),'db/user.json')
        #user_db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))
        #user_db.insert({'type': 'apple', 'count': 7})
