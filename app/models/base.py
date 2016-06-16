# -*- coding: utf-8 -*-

import functools
import os
import sys
import weakref
import datetime
import bson


from app.error import InvalidError
from app.db import db


class ModelError(InvalidError):
    pass


class ModelDeclareError(ModelError):
    pass


class ModelInvaldError(InvalidError):
    pass


class Field(object):
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
        if sort:
            cursor = cursor.sort(sort)
        if offset:
            cursor = cursor.skip(offset)
        if limit:
            cursor = cursor.limit(limit)

        return map(lambda x: cls(x), cursor), cursor.count()

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
        """ a format dictionary.
        """
        return self._attrs



