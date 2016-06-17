# -*- coding: utf-8 -*-
import os
import sys
import datetime
from collections import namedtuple

import unittest
from app.config import config
from app.db import db
from app.models import ModelError, ModelInvaldError, ModelDeclareError
from app.models import Meta, Base, ClassReadonlyProperty
from app.models import Field, IDField, StringField, BoolField, IntField, DateField, ListField, TupleField


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

    def test_exception(self):
        class Foo(Base):
            _table = ClassReadonlyProperty('foo')
            _primary_key = ClassReadonlyProperty('_id')

            _id = IDField()
            str_field = StringField()
            default_str_field = StringField(default_value='hello')

            date_field = DateField()
            int_field = IntField()
            bool_field = BoolField()
            list_field = ListField()
            tuple_field = TupleField(namedtuple('Point',['x', 'y'], False), {'x': 0, 'y':0})

        self.assertEqual(Foo._primary_key, '_id')
        self.assertEqual(Foo._table, 'foo')

        foo = Foo()
        self.assertTrue(foo.is_new())
        self.assertEqual(foo.default_str_field, 'hello')

        foo = Foo.create({'str_field': 'bar'})
        self.assertFalse(foo.is_new())
        self.assertIsNotNone(foo._id)
        self.assertEqual(foo.str_field, 'bar')
        self.assertEqual(foo.int_field, 0)

        foo.int_field = 100
        self.assertEqual(foo.int_field, 100)

        foo.int_field = '200'
        self.assertEqual(foo.int_field, 200)

        self.assertIsInstance(foo.date_field, datetime.date)
        foo.date_field = datetime.datetime(2016, 12, 01, 1, 2, 3, 4)
        self.assertEqual(foo.date_field, datetime.date(2016, 12, 1))
        with self.assertRaises(ModelInvaldError):
            foo.date_field = 1234

        self.assertEqual(foo.list_field, [])
        foo.list_field = [0, 1, 2, 3]
        self.assertEqual(foo.list_field, [0, 1, 2, 3])

        foo.save()

        _foo = db.foo.find_one({'_id': foo._id})
        self.assertEqual(_foo, foo._attrs)

        with self.assertRaises(ModelError) as ctx:
            foo = Foo.create({'other': 'other'})

        with self.assertRaises(ModelDeclareError) as ctx:
            class Foo1(Base):
                pass

        with self.assertRaises(ModelDeclareError) as ctx:
            class Foo2(Base):
                _id = IDField()
                _id_2 = IDField()

    def test_fetch(self):
        class Foo(Base):
            _table = ClassReadonlyProperty('foo')
            _primary_key = ClassReadonlyProperty('_id')

            _id = IDField()
            name = StringField()
            age = IntField()

        foos = [{
            'name': 'Bill',
            'age': 10,
        }, {
            'name': 'John',
            'age': 30
        }, {
            'name': 'Mary',
            'age': 20
        }, {
            'name': 'Tommy',
            'age': 40
        }]
        for foo in foos:
            Foo.create(foo)

        r = Foo.fetch({})
        self.assertEqual(r.total, 4)
        self.assertItemsEqual([f.name for f in r], [f['name'] for f in foos])

        r = Foo.fetch({'age': {'$gt': 20}})
        self.assertEqual(r.total, 2)
        self.assertTrue(r[0].age > 20)
        self.assertTrue(r[1].age > 20)


        r = Foo.fetch({'name': 'John'})
        self.assertEqual(r.total, 1)
        self.assertEqual(r[0].name, 'John')


