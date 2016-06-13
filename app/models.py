# -*- coding: utf-8 -*-

import functools
import os
import sys
import weakref
import datetime
import bson


from app.error import InvalidError
from app.db import db


class Field(object):
    field_key = None

    def __init__(self):
        pass

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
        return None

    def value_in(self, instance, value):
        """The process from property to assign value in instance._attrs"""
        return value

    def value_out(self, instance, value):
        """The process from value in instance._attrs to property."""
        return value

    #def value_to_json(self, instance, value):
    # mabey is a good idea. to declare a value that can from db to json


class IDField(Field):
    @classmethod
    def generate_id(cls):
        return str(bson.ObjectId())


class StringField(Field):
    def value_default(self, instance):
        return ''

    def value_in(self, instance, value):
        return str(value)

    def value_out(self, instance, value):
        return value


class DateField(Field):
    def value_default(self, instance):
        return '1900-01-01'

    def value_in(self, instance, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError('`DateField` only accept `date` value')
        return value

    def value_out(self, instance, value):
        return value


class ListField(Field):
    def value_default(self, instance):
        return []


class ConfigAttr(object):
    def __init__(self):
        self.values = {}

    def __get__(self, instance, cls):
        if cls not in self.values:
            self.values[cls] = {}
        return self.values[cls]

    def __set__(self, instance, value):
        raise Exception('`ConfigAttr` is readonly.')


class AttrsAttr(object):
    def __init__(self):
        self.values = weakref.WeakKeyDictionary()

    def __get__(self, instance, cls):
        if instance:
            if instance not in self.values:
                self.values[instance] = {}
            return self.values[instance]
        raise Exception('AttrsAttr can not work on class level.')

    def __set__(self):
        raise Exception('`AttrsAttr` is readonly.')


class Meta(type):
    def __init__(cls, cls_name, cls_bases, cls_dict):
        # cls = type.__new__(meta_cls, cls_name, cls_bases, cls_dict)
        for field_key, field in cls_dict.items():
            if isinstance(field, Field):
                field.register(cls, field_key)


class Base(object):
    __metaclass__ = Meta
    _config = ConfigAttr()
    _attrs = AttrsAttr()

    @classmethod
    def get_one(cls, _id=None):
        row = db[cls._table].find_one({'_id': _id})
        return cls(row)

    @classmethod
    def find(cls, query={}, return_cursr=False):
        """find instances by query.

        :param dict query:
        :param function process: a function procss cursor, ex skip, limit, sort. ex: lambda c: c.sort().skip(100).limit(10)

        """
        root_cursor = db[cls._table].find(query)
        cursor = process(root_cursor)
        if return_cursor:
            return cursor

        for row in cursor:
            yield cls(row)


    @classmethod
    def _insert_one(cls, payload):
        """Proxy to db.collection.insert_one."""
        result = db[cls._table].insert_one(payload)
        if not result.inserted_id:
            raise Exception('create instance fail.')
        return result.inserted_id

    @classmethod
    def _update_one(cls, query={}, payload={}):
        """Proxy to db.collection.update_one."""
        if not query:
            raise error.InvalidError('can update by empty query.')

        if not payload:
            raise error.InvalidError('can update by empty payload.')

        result = db[cls._table].update_one(query, {
            '$set': payload
        })

        if result.matched_count == 1:
            return True
        else:
            return False


    @classmethod
    def create(cls, payload={}):
        person = cls(payload)
        person.save()
        return person


    def __init__(self, _attrs={}):
        self._attrs.update(_attrs)

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
        return self._attrs


class Person(Base):
    _table = 'persons'
    _id = IDField()

    social_id = StringField()
    name = StringField()
    birthday = DateField()
    gender = StringField()

    phone_0 = StringField()
    phone_1 = StringField()
    phone_2 = StringField()

    address_0 = StringField()
    address_1 = StringField()

    email_0 = StringField()
    email_1 = StringField()

    education = StringField()
    job = StringField()

    register_date = StringField()
    unregister_date = StringField()

    baptize_date = StringField()
    baptize_priest = StringField()

    gifts = ListField()     # ['aa', 'bb', 'cc']
    groups = ListField()    # [group_id, group_id, group_id]
    events = ListField()    # {date:'', 'title': 'bala...'}
    relations = ListField()  # {rel: 'parent', _id: '1231212'}

    note = StringField()

    def get_relations(self):
        _ids = [row['_id'] for row in self.relations]
        return Person.find({'_id': {'$in': ids}})

    @classmethod
    def build_relation(cls, rel, p1, p2):
        p1.relations.append({
            'rel': rel,
            '_id': p2._id
        })
        p2.relations.append({
            'rel': rel,
            '_id': p1._id
        })
        p1.save()
        p2.save()


class Group(Base):
    _table = 'groups'

    _id = IDField()
    name = Field()
