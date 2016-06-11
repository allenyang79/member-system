# -*- coding: utf-8 -*-
import os
import sys
import unittest
import datetime

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
        db.tests.insert_one({'name': 'test-name'})
        r = db.tests.find_one({'name': 'test-name'})
        self.assertEqual(r['name'], 'test-name')

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

        p.birthday = datetime.datetime.strptime('2016-11-12','%Y-%m-%d')
        print p.birthday
        print p.attrs
        p.save()

        raw = db.persons.find_one({'_id': p.get_id()})
        print raw
        return
        self.assertEqual(raw['name'], 'Bill')
        self.assertEqual(raw['phone_0'], '0988')

        _p = Person.get_one(p.get_id())
        self.assertEqual(_p.attrs, p.attrs)

        p_other = Person.create({
            'name': 'Mary'
        })

        Person.build_relation('family', p, p_other)
        _p = Person.get_one(p.get_id())
        self.assertIn({
            'rel': 'family',
            '_id': p_other.get_id()
        }, p.relations)

        _p_other = Person.get_one(p_other.get_id())
        self.assertIn({
            'rel': 'family',
            '_id': p.get_id()
        }, _p_other.relations)




    def test_group(self):
        g = Group.create({
            'name': 'group-01'
        })
        self.assertEqual(g.name, 'group-01')
