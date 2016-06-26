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
        """ Test basic db operator. """
        db.tests.insert_one({'name': 'test-name'})
        r = db.tests.find_one({'name': 'test-name'})
        self.assertEqual(r['name'], 'test-name')

        db.tests.insert_one({'_id': '_id', 'a': 'A', 'b': 'B', 'c': 'c'})

    def test_operator(self):
        """ Test declare a ModelClass. """
        Point = namedtuple('Point', ['x', 'y'], False)

        class Foo(Base):
            _table = ClassReadonlyProperty('foos')
            _primary_key = ClassReadonlyProperty('foo_id')

            foo_id = IDField('_id')
            str_field = StringField()
            default_str_field = StringField(default='hello')
            date_field = DateField()
            int_field = IntField()
            bool_field = BoolField()
            list_field = ListField()

            tuple_field = TupleField(np=Point, default=lambda: Point(x=0, y=0))

        for field_key in ('foo_id', 'str_field', 'default_str_field', 'date_field', 'int_field', 'bool_field', 'list_field', 'tuple_field'):
            self.assertIn(field_key, Foo._config)

        class Bar(Base):
            _table = ClassReadonlyProperty('bars')
            _primary_key = ClassReadonlyProperty('_id')

        self.assertNotEqual(Foo._config, Bar._config)

        self.assertEqual(Foo._primary_key, 'foo_id')
        self.assertEqual(Foo._table, 'foos')
        self.assertEqual(Foo.foo_id.raw_field_key, '_id')

        foo = Foo()
        self.assertEqual(foo._config, Foo._config)
        self.assertTrue(foo.is_new())
        self.assertEqual(foo.default_str_field, 'hello')

        foo = Foo.create({'str_field': 'any string'})
        self.assertFalse(foo.is_new())
        self.assertIsNotNone(foo.foo_id)
        self.assertEqual(foo.str_field, 'any string')
        self.assertEqual(foo.int_field, 0)

        foo.int_field = 100
        self.assertEqual(foo.int_field, 100)

        foo.int_field = '200'
        self.assertEqual(foo.int_field, 200)

        self.assertIsNone(foo.date_field)
        foo.date_field = datetime.datetime(2016, 12, 01, 1, 2, 3, 4)
        self.assertEqual(foo.date_field, datetime.date(2016, 12, 1))

        self.assertEqual(foo.list_field, [])
        foo.list_field = [0, 1, 2, 3]
        self.assertEqual(foo.list_field, [0, 1, 2, 3])

        foo.str_field = None
        self.assertEqual(foo._attrs['str_field'], None)
        foo.save()

        _foo = db.foos.find_one({'_id': foo.foo_id})
        self.assertEqual(_foo, foo._attrs)





        with self.assertRaises(ModelInvaldError):
            foo.date_field = 1234

        with self.assertRaises(ModelError) as ctx:
            foo = Foo.create({'other': 'other'})


    def test_jsonify_encode(self):
        """ Test jsonify encode to dict for json dumps."""

        Point = namedtuple('Point', ['x', 'y'], False)

        class Foo(Base):
            _table = ClassReadonlyProperty('foos')
            _primary_key = ClassReadonlyProperty('foo_id')

            foo_id = IDField('_id')
            str_field = StringField(default='this is default')
            date_field = DateField()
            int_field = IntField()
            bool_field = BoolField()
            list_field = ListField()
            tuple_field = TupleField(np=Point)

        foo = Foo.create({
            'int_field': 100,
            'list_field': [1, 2, 3],
        })

        _foo = foo.to_jsonify()
        self.assertEqual('Foo', _foo['__class__'])
        self.assertEqual(_foo['foo_id'], foo.foo_id,)
        self.assertEqual(_foo['str_field'], 'this is default')
        self.assertEqual(_foo['int_field'], 100)
        self.assertEqual(_foo['list_field'], [1, 2, 3])
        self.assertNotIn('tuple_field', _foo)
        self.assertNotIn('date_field', _foo)

        Point = namedtuple('Point', ['x', 'y'], False)

        class Foo(Base):
            _table = ClassReadonlyProperty('foos')
            _primary_key = ClassReadonlyProperty('foo_id')

            foo_id = IDField('_id')
            list_field = ListField()
            tuple_field = TupleField(np=Point, default=lambda: Point(x=1, y=2))

        foo = Foo.create({})
        _foo = foo.to_jsonify()
        self.assertEqual(_foo['tuple_field'], {'x': 1, 'y': 2})
        self.assertEqual(_foo['list_field'], [])


    def test_jsonify_decode(self):
        """ Test jsonify decode from dict for json loads."""

        Point = namedtuple('Point', ['x', 'y'], False)
        class Foo(Base):
            _table = ClassReadonlyProperty('foos')
            _primary_key = ClassReadonlyProperty('foo_id')

            foo_id = IDField('_id')
            str_field = StringField(default='this is default')
            date_field = DateField()
            int_field = IntField()
            bool_field = BoolField()
            list_field = ListField()
            tuple_field = TupleField(np=Point)

        json_str = '''{
            "__class__": "Foo",
            "foo_id": "1234",
            "str_field": "anything",
            "int_field": 123,
            "date_field": "2014-12-13",
            "bool_field": false,
            "tuple_field":{
                "x": 1,
                "y": 2
            }
        }'''
        foo = Foo.from_jsonify(json.loads(json_str))

        self.assertEqual(foo.foo_id, '1234')
        self.assertEqual(foo.int_field, 123)
        self.assertEqual(foo.bool_field, False)
        self.assertEqual(foo.date_field, datetime.date(2014, 12, 13))
        Point = namedtuple('Point', ['x', 'y'], False)
        self.assertEqual(foo.tuple_field, Point(x=1, y=2))

    def test_declare_error(self):
        """ Test by error case."""

        with self.assertRaises(ModelDeclareError) as ctx:
            class Foo(Base):
                pass

        with self.assertRaises(ModelDeclareError) as ctx:
            class Foo(Base):
                _id = IDField()
                _id_2 = IDField()

    def test_fetch(self):
        """Test fetch by Model."""

        class Foo(Base):
            _table = ClassReadonlyProperty('foos')
            _primary_key = ClassReadonlyProperty('_id')

            _id = IDField()
            name = StringField()
            age = IntField()

        foos = [{
            '_id': 'id_0',
            'name': 'Bill',
            'age': 10,
        }, {
            '_id': 'id_1',
            'name': 'John',
            'age': 30
        }, {
            '_id': 'id_2',
            'name': 'Mary',
            'age': 20
        }, {
            '_id': 'id_3',
            'name': 'Tommy',
            'age': 40
        }]
        db.foos.insert_many(foos)

        r = Foo.fetch({})
        self.assertEqual(r.total, 4)
        self.assertItemsEqual([f.name for f in r], [f['name'] for f in foos])

        r = Foo.fetch({'_id': 'id_2'})
        self.assertEqual(r.total, 1)
        self.assertEqual(r[0]._id, 'id_2')
        self.assertEqual(r[0].name, 'Mary')
        self.assertEqual(r[0].age, 20)

        r = Foo.fetch({'age': {'$gt': 20}})
        self.assertEqual(r.total, 2)
        self.assertTrue(r[0].age > 20)
        self.assertTrue(r[1].age > 20)

        r = Foo.fetch({'name': 'John'})
        self.assertEqual(r.total, 1)
        self.assertEqual(r[0].name, 'John')
