# -*- coding: utf-8 -*-
import os
import sys
import unittest

from app.config import config
from app.db import db


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_db(self):
        db.test.insert_one({'name': 'test'})
        r = db.test.find_one({'name': 'test'})
        print r
