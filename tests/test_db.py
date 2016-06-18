# -*- coding: utf-8 -*-
import os
import sys
from app.config import config
#from app.db import db
from app.db import db
import unittest


class TestDB(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_db(self):
        db.tests.insert_one({'_id': '1234'})
        one = db.tests.find_one()
        self.assertTrue(one)
        db.tests.drop()
