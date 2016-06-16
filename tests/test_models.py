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
        return
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

        _p = Person.get_one(p.get_id())
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

        persons, _ = Person.fetch()
        for p in persons:
            self.assertIsInstance(p, Person)


    def test_group(self):
        return
        g = Group.create({
            'name': 'group-01'
        })
        self.assertEqual(g.name, 'group-01')
