# -*- coding: utf-8 -*-
import os
import sys
import datetime
import unittest

from app.config import config
from app.db import db
from app.models.models import Person
from app.models.models import Group


class TestModel(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_person(self):
        """Person"""
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

        p.birthday = datetime.datetime.strptime('2016-11-12', '%Y-%m-%d')
        p.save()

        raw = db.persons.find_one({'_id': p.get_id()})
        self.assertEqual(raw['name'], 'Bill')
        self.assertEqual(raw['phone_0'], '0988')
        self.assertEqual(raw['birthday'], datetime.datetime.strptime('2016-11-12', '%Y-%m-%d'))

        with self.assertRaises(Exception) as ctx:
            # can only assign datetime object to `birthday`
            p.birthday = 'anything'

        p = Person.get_one(p.get_id())
        p_other = Person.create({
            'name': 'Mary'
        })
        p.build_relation('family', p_other.get_id(), due=True)

        p = Person.get_one(p.get_id())
        self.assertIn({
            'rel': 'family',
            'person_id': p_other.get_id()
        }, p.relations)

        p_other = Person.get_one(p_other.get_id())
        self.assertIn({
            'rel': 'family',
            'person_id': p.get_id()
        }, p_other.relations)

        # test fetch
        fetch_result = Person.fetch()
        self.assertEqual(fetch_result.total, 2)
        for p in fetch_result:
            self.assertIsInstance(p, Person)

    def test_group(self):
        """Group"""
        payload = {
            'name': 'group-01',
            'note': 'this is my group'
        }
        g = Group.create(payload)

        self.assertEqual(g.name, payload['name'])
        self.assertEqual(g.note, payload['note'])

        raw = db.groups.find_one({'_id': g.get_id()})
        self.assertEqual(g.name, raw['name'])
        self.assertEqual(g.note, raw['note'])

        g.name = 'group-01-fix'
        g.save()

        raw = db.groups.find_one({'_id': g.get_id()})
        self.assertEqual(g.name, 'group-01-fix')
