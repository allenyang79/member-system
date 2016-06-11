# -*- coding: utf-8 -*-
import os
import sys
import unittest

from app.config import config
from app.db import db
#import app.models as models
from app.models import Person
from app.models import Group


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_db(self):
        db.test.insert_one({'name': 'test'})
        r = db.test.find_one({'name': 'test'})
        self.assertEqual(r['name'], 'test')

    def test_person(self):
        p = Person.create({
            'name': 'John',
            'phone_0': '0988'
        })
        self.assertEqual(p.name, 'John')
        self.assertEqual(p.phone_0, '0988')

        p.name = 'Bill'
        self.assertEqual(p.name, 'Bill')

        p.phone_1 = '0989'
        self.assertEqual(p.phone_1, '0989')

        p.save()

        raw = db.persons.find_one({'_id': p.get_id()})
        self.assertEqual(raw['name'], 'Bill')
        self.assertEqual(raw['phone_0'], '0988')

        p2 = Person.get_one(p.get_id())
        self.assertEqual(p2.attrs, p.attrs)

    def test_group(self):
        g = Group.create({
            'name': 'group-01'
        })

        self.assertEqual(g.name, 'group-01')
