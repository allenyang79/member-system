# -*- coding: utf-8 -*-
import json
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
    def tearDown(self):
        for col_name in db.collection_names():
            db[col_name].drop()

    def test_db(self):
        db.tests.insert_one({'name': 'test-name'})
        r = db.tests.find_one({'name': 'test-name'})
        self.assertEqual(r['name'], 'test-name')

    def test_operator(self):
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

        for field_key in ('_id', 'str_field', 'default_str_field', 'date_field', 'int_field', 'bool_field', 'list_field', 'tuple_field'):
            self.assertIn(field_key, Foo._config)

        class Bar(Base):
            _table = ClassReadonlyProperty('bar')
            _primary_key = ClassReadonlyProperty('_id')

        self.assertNotEqual(Foo._config, Bar._config)


        self.assertEqual(Foo._primary_key, '_id')
        self.assertEqual(Foo._table, 'foo')

        foo = Foo()
        self.assertEqual(foo._config, Foo._config)

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


        _foo = foo.to_dict()

        self.assertEqual('Foo', _foo['__class__'])
        self.assertEqual(foo._id, _foo['_id'])
        self.assertEqual(foo.int_field, _foo['int_field'])
        self.assertEqual(foo.date_field.strftime('%Y-%m-%d'), _foo['date_field'])

        # it should be encode
        json.dumps(_foo)


        json_str = '''{
            "__class__": "Foo",
            "_id": "1234",
            "int_field": 123,
            "date_field": "2014-12-13",
            "bool_field": false,
            "tuple_field":{
                "x": 1,
                "y": 2
            }
        }'''
        _foo = Foo.from_dict(json.loads(json_str))
        self.assertEqual(_foo._id, '1234')
        self.assertEqual(_foo.int_field, 123)
        self.assertEqual(_foo.bool_field, False)
        self.assertEqual(_foo.date_field, datetime.date(2014, 12, 13))
        Point = namedtuple('Point',['x', 'y'], False)
        self.assertEqual(_foo.tuple_field, Point(x=1,y=2))

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
        return
        class Foo3(Base):
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
            Foo3.create(foo)

        r = Foo3.fetch({})
        self.assertEqual(r.total, 4)
        self.assertItemsEqual([f.name for f in r], [f['name'] for f in foos])

        r = Foo3.fetch({'age': {'$gt': 20}})
        self.assertEqual(r.total, 2)
        self.assertTrue(r[0].age > 20)
        self.assertTrue(r[1].age > 20)


        r = Foo3.fetch({'name': 'John'})
        self.assertEqual(r.total, 1)
        self.assertEqual(r[0].name, 'John')


