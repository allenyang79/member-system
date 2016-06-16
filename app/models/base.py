# -*- coding: utf-8 -*-

import functools
import os
import sys
import weakref
import datetime
import bson
from collections import namedtuple

from app.error import InvalidError
from app.db import db


class ModelError(InvalidError):
    """Base model operator error."""
    pass


class ModelDeclareError(ModelError):
    """Error on declare a new Model"""
    pass


class ModelInvaldError(InvalidError):
    """Invalid model operator."""
    pass


class Field(object):
    """Decalre a propery for Model"""
    field_key = None

    def __init__(self, default_value=None):
        self.default_value = default_value

    def __get__(self, instance, cls):
        if instance:
            if self.field_key not in instance._attrs:
                instance._attrs[self.field_key] = self.value_default(instance)
            return self.value_out(instance, instance._attrs[self.field_key])
        return self

    def __set__(self, instance, value):
        instance._attrs[self.field_key] = self.value_in(instance, value)

    def register(self, cls, field_key):
        self.field_key = field_key
        cls._config[field_key] = self

    def value_default(self, instance):
        """The default value of this field."""
        return self.default_value

    def value_in(self, instance, value):
        """The process from property to assign value in instance._attrs"""
        return value

    def value_out(self, instance, value):
        """The process from value in instance._attrs to property."""
        return value

    # def value_to_json(self, instance, value):
    # mabey is a good idea. to declare a value that can from db to json


class IDField(Field):
    @classmethod
    def generate_id(cls):
        return str(bson.ObjectId())


class StringField(Field):
    def __init__(self, default_value=''):
        self.default_value = default_value

    def value_in(self, instance, value):
        return str(value)

    def value_out(self, instance, value):
        return value


class BoolField(Field):
    def __init__(self, default_value=False):
        self.default_value = default_value

    def value_in(self, instance, value):
        return bool(value)

    def value_out(self, instance, value):
        return value


class IntField(Field):
    def __init__(self, default_value=0):
        self.default_value = default_value

    def value_in(self, instance, value):
        return int(value)

    def value_out(self, instance, value):
        return value


class DateField(Field):
    def __init__(self, default_value=datetime.datetime(1900, 1, 1).replace(minute=0, hour=0, second=0, microsecond=0)):
        self.default_value = default_value

    def value_in(self, instance, value):
        if isinstance(value, datetime.date):
            return datetime.datetime.combine(value, datetime.datetime.min.time())
        elif isinstance(value, datetime.datetime):
            return value.replace(minute=0, hour=0, second=0, microsecond=0)
        raise ModelInvaldError('`DateField` only accept `date` value')

    def value_out(self, instance, value):
        return value.date()


class ListField(Field):
    def __init__(self, default_value=[]):
        self.default_value = default_value

    def value_in(self, instance, value):
        return list(value)


class TupleField(Field):
    def __init__(self, np, kw):
        self.np = np  # namedtuple('Point', ['x', 'y'], verbose=True)
        self.default_value = kw#self.np(**kw)

    def value_in(self, instance, value):
        return value.__dict__

    def value_out(self, instance, value):
        return self.np(**value)


class ClassReadonlyProperty(object):
    """a propery declare on class, and it is readonly and share with all instance.
    It is good to declare _table or _config.
    """

    def __init__(self, default_value=None):
        self.value = default_value

    def __get__(self, instance, cls):
        return self.value

    def __set__(self, instance, value):
        raise ModelInvaldError('`ClassReadonlyProperty` is readonly.')


class AttrsAttr(object):
    def __init__(self):
        self.values = weakref.WeakKeyDictionary()

    def __get__(self, instance, cls):
        if instance:
            if instance not in self.values:
                self.values[instance] = {}
            return self.values[instance]
        raise ModelInvaldError('AttrsAttr can not work on class level.')

    def __set__(self):
        raise ModelInvaldError('`AttrsAttr` is readonly.')


class Meta(type):
    def __init__(cls, cls_name, cls_bases, cls_dict):
        # cls = type.__new__(meta_cls, cls_name, cls_bases, cls_dict)
        if cls_name == 'Base':
            return
        primary_key_exists = False
        for field_key, field in cls_dict.items():
            if isinstance(field, Field):
                field.register(cls, field_key)
                if isinstance(field, IDField):
                    if primary_key_exists:
                        raise ModelDeclareError('model %s can not set primary_key `%s` twice.' % (cls_name, field_key))
                    primary_key_exists = True

            if cls._table is None:
                raise ModelDeclareError('declare Moedl without _table.')

            if cls._primary_key is None:
                raise ModelDeclareError('declare Moedl without IDField.')


class FetchResult(object):
    def __init__(self, cls, cursor):
        self.cls = cls
        self.root_cursor = cursor
        self.cursor = self.root_cursor.clone()

    def __iter__(self):
        return self

    def __getitem__(self, key):
        return self.cls(self.cursor[key])

    def next(self):
        return self.cls(next(self.cursor))

    def sort(self, key, sort):
        self.cursor = self.cursor.sort(key, sort)
        return self

    def limit(self, limit):
        self.cursor = self.cursor.limit(limit)
        return self

    def skip(self, skip):
        self.cursor = self.cursor.skip(skip)
        return self

    def rewind(self):
        self.cursor.rewind()
        return self

    def reset(self):
        self.cursor = self.root_cursor.clone()
        return self

    @property
    def total(self):
        return self.root_cursor.count()


class Base(object):
    __metaclass__ = Meta
    _config = ClassReadonlyProperty(default_value={})
    _attrs = AttrsAttr()

    _table = ClassReadonlyProperty()
    _primary_key = ClassReadonlyProperty()

    @classmethod
    def _find(cls, query={}):
        """Proxy to db.collection.find."""
        return db[cls._table].find(query)

    @classmethod
    def _insert_one(cls, payload):
        """Proxy to db.collection.insert_one."""
        result = db[cls._table].insert_one(payload)
        if not result.inserted_id:
            raise ModelInvaldError('create instance fail.')
        return result.inserted_id

    @classmethod
    def _update_one(cls, query={}, payload={}):
        """Proxy to db.collection.update_one."""
        if not query:
            raise ModelInvaldError('can update by empty query.')

        if not payload:
            raise ModelInvaldError('can update by empty payload.')

        result = db[cls._table].update_one(query, {
            '$set': payload
        })

        if result.matched_count == 1:
            return True
        else:
            return False

    @classmethod
    def get_one(cls, _id=None):
        row = db[cls._table].find_one({'_id': _id})
        return cls(row)

    @classmethod
    def create(cls, payload={}):
        person = cls(payload)
        person.save()
        return person

    @classmethod
    def fetch(cls, query={}, sort=None, offset=None, limit=None):
        cursor = cls._find(query)
        return FetchResult(cls, cursor)

    @classmethod
    def fetch_all(cls, query={}):
        cursor = cls._find(query)
        for row in cursor:
            yield cls(row)

    def __init__(self, _attrs={}):
        # self._attrs.update(_attrs)
        for k, v in _attrs.items():
            if k not in self._config:
                raise ModelError('init model instancewith unfield value.')
            setattr(self, k, v)

    def is_new(self):
        if '_id' in self._attrs:
            return False
        return True

    def get_id(self):
        return self._attrs['_id']

    def save(self, allow_fields=None):
        """Save _attrs in to database.

        :param list allow_fields: it will only save allow_fields.
        """
        cls = type(self)
        payload = {}

        fields = set(self._config.keys())
        if allow_fields:
            fields = allow_fields & fields

        for k in fields:
            if self.is_new() and isinstance(self._config[k], IDField):
                pass  # pass if primary_key
            if k in self._attrs:
                payload[k] = self._attrs[k]

        if self.is_new():
            payload['_id'] = IDField.generate_id()
            self._attrs['_id'] = cls._insert_one(payload)
        else:
            cls._update_one({'_id': self.get_id()}, payload)

    def to_dict(self):
        """ return a standand dict.
        """
        return self._attrs
