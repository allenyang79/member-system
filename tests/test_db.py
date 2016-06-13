# -*- coding: utf-8 -*-
import os
import sys
import datetime
import unittest

from app.config import config
from app.db import db
from app.models import Meta, Base
from app.models import Field, IDField, StringField, IntField, DateField, ListField


class TestDB(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        for col_name in db.collection_names():
            db[col_name].drop()

    def test_db(self):
        db.tests.insert_one({'name': 'test-name'})
        r = db.tests.find_one({'name': 'test-name'})
        self.assertEqual(r['name'], 'test-name')



    def test_base(self):

        class Student(Base):
            _table='students'
            _id = IDField()
            name = StringField()
            age = IntField()
            birthday = DateField()
            tags = ListField()

        s = Student.create({
            'name': 'Bill',
            'age' : 10,
            'birthday': datetime.datetime(2016,6,2),
            'tags': ['a','b','c']
        })

        self.assertEqual(s.name, 'Bill')
        self.assertEqual(s.age, 10)
        self.assertEqual(s.birthday, datetime.datetime(2016,6,2))
        self.assertEqual(['a', 'b', 'c'], s.tags)

        s.tags.append('d')
        self.assertIn('d', s.tags)
        s.save()


        with self.assertRaises(Exception) as ctx:
            s.birthday = 1234



        s2 = Student.create({
            'name': 'John'
        })
        rows, total = Student.fetch({'name': 'John'})
        self.assertEqual(rows[0].name, 'John')

        ss = Student.get_one(s._id)
        self.assertEqual(ss._attrs, s._attrs)


        self.assertEqual(s.to_dict(), {
            '_id': s._id,
            'name': s.name,
            'age': s.age,
            'tags': s.tags,
            'birthday': s.birthday
        })
