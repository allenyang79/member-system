# -*- coding: utf-8 -*-

import copy
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


class ModelParserError(InvalidError):
    """Parse from dict fail."""
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

    # process value in/out of db
    def value_default(self, instance):
        """The default value of this field."""
        return self.default_value

    def value_in(self, instance, value):
        """The value from external to instance._attrs"""
        return value

    def value_out(self, instance, value):
        """The value from instance._attrs to external"""
        return value

    def encode(self, value):
        """ encode external value to another data type that json.dumps can process. """
        return value

    def decode(self, value):
        """ decode external value from another data type that json.loads can process. """
        return value


class IDField(Field):
    def is_new(self, instance):
        if self.field_key not in instance._attrs:
            return True
        if not instance._attrs[self.field_key]:
            return True
        return False

    def generate_id(self, instance):
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

    def encode(self, value):
        return value.strftime('%Y-%m-%d')

    def decode(self, value):
        return datetime.datetime.strptime(value, '%Y-%m-%d')


class ListField(Field):
    def value_in(self, instance, value):
        return list(value)

    def value_default(self, instance):
        """The default value of this field."""
        return []


class TupleField(Field):
    def __init__(self, np, kw):
        self.np = np  # namedtuple('Point', ['x', 'y'], verbose=True)
        self.default_value = kw  # self.np(**kw)

    def value_in(self, instance, value):
        return value.__dict__

    def value_out(self, instance, value):
        if isinstance(value, dict):
            return self.np(**value)
        return None

    def encode(self, value):
        return value.__dict__

    def decode(self, value):
        return self.np(**value)


class ClassReadonlyProperty(object):
    """a propery declare on class, and it is readonly and share with all instance.
    It is good to declare _table or _config.
    """

    def __init__(self, default_value=lambda: None):
        self.default_value = default_value
        self.values = weakref.WeakKeyDictionary()

    def __get__(self, instance, cls):
        if cls not in self.values:
            if hasattr(self.default_value, '__call__'):
                self.values[cls] = self.default_value()
            else:
                self.values[cls] = self.default_value

        return self.values[cls]

    def __set__(self, instance, value):
        raise ModelInvaldError('`ClassReadonlyProperty` is readonly.')


class InstanceReadonlyProperty(object):
    def __init__(self, default_value=lambda: None):
        self.default_value = default_value
        self.values = weakref.WeakKeyDictionary()

    def __get__(self, instance, cls):
        if instance:
            if instance not in self.values:
                if hasattr(self.default_value, '__call__'):
                    self.values[instance] = self.default_value()
                else:
                    self.values[instance] = self.default_value
            return self.values[instance]
        raise ModelInvaldError('`InstanceReadonlyProperty` can not work on class level.')

    def __set__(self):
        raise ModelInvaldError('`InstanceReadonlyProperty` is readonly.')


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

    _config = ClassReadonlyProperty(lambda: {})
    _attrs = InstanceReadonlyProperty(lambda: {})

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

    def __init__(self, _attrs={}):
        # self._attrs.update(_attrs)
        for k, v in _attrs.items():
            if k not in self._config:
                raise ModelError('init model instancewith unfield value.')
            setattr(self, k, v)

    def is_new(self):
        primary_field = self._config[self._primary_key]
        return primary_field.is_new(self)

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
            fields = set(allow_fields) & fields

        for k in fields:
            if self.is_new() and isinstance(self._config[k], IDField):
                pass  # pass if primary_key
            if k in self._attrs:
                payload[k] = self._attrs[k]

        if self.is_new():
            primary_field = self._config[self._primary_key]
            payload['_id'] = primary_field.generate_id(self)
            self._attrs['_id'] = cls._insert_one(payload)
        else:
            cls._update_one({'_id': self.get_id()}, payload)

    def to_dict(self, use_raw=False):
        """ return a dict, that can be dump to json.
        :param bool use_raw: if True, it will return a copy of self._attrs.

        """
        if use_raw:
            return copy.deepcopy(self._attrs)

        ret = {
            '__class__': type(self).__name__
        }
        for field_key, field in self._config.iteritems():
            if field_key in self._attrs:
                ret[field_key] = field.encode(getattr(self, field_key))
        return ret

    def update(self, payload, use_raw=False):
        """update a value from external dict by json.loads()."""
        if use_raw:
            self._attrs.update(payload)
            return self

        for field_key, field in self._config.iteritems():
            if field_key in payload:
                setattr(self, field_key, field.decode(payload[field_key]))
        return self

    @classmethod
    def from_dict(cls, payload):
        if '__class__' in payload and payload['__class__'] == cls.__name__:
            raw = {}
            for field_key, field in cls._config.iteritems():
                if field_key in payload:
                    raw[field_key] = field.decode(payload[field_key])
            return cls(raw)
        raise ModelParserError('can not parse `%s` to `%s` instance.' % (payload, cls.__name__))
