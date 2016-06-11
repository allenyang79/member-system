import os
import sys
import weakref
import datetime

from app.db import db


class InvalidError(Exception):
    def __init__(self, message):
        super(InvalidError, self).__init__(message)


class Field(object):
    def __get__(self, instance, cls):
        if instance:
            if self.field_key in instance.attrs:
                return instance.attrs[self.field_key]
            else:
                return None

    def __set__(self, instance, value):
        instance.attrs[self.field_key] = value

    def _register(self, cls, field_key):
        self.field_key = field_key
        cls._config[field_key] = self


class IDField(Field):
    pass


class IntField(Field):
    def __get__(self, instance, cls):
        if instance:
            if self.field_key not in instance.attrs:
                instance.attrs[self.field_key] = 0
            return instance.attrs[self.field_key]

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise InvalidError('`IntField` must assign a `int` value')
        instance.attrs[self.field_key] = int(value)


class StringField(Field):
    def __get__(self, instance, cls):
        if instance:
            if self.field_key not in instance.attrs:
                instance.attrs[self.field_key] = ''
            return instance.attrs[self.field_key]

    def __set__(self, instance, value):
        if not isinstance(value, basestring):
            raise InvalidError('`StringField` must assign a `string` value')
        instance.attrs[self.field_key] = str(value)

class DateField(Field):
    def __get__(self, instance, cls):
        if instance:
            if self.field_key not in instance.attrs:
                instance.attrs[self.field_key] = None
            return instance.attrs[self.field_key]

    def __set__(self, instance, value):
        if not isinstance(value, datetime.datetime):
            raise InvalidError('`DateField` must assign a `Date` value')
        instance.attrs[self.field_key] = value


class ListField(Field):
    def __get__(self, instance, cls):
        if instance:
            if self.field_key not in instance.attrs:
                instance.attrs[self.field_key] = []
            return instance.attrs[self.field_key]

    def __set__(self, instance, value):
        if not isinstance(value, iter):
            raise InvalidError('`ListField` must assign a `iter` value')
        instance.attrs[self.field_key] = list(value)


class DictField(Field):
    def __get__(self, instance, cls):
        if instance:
            if self.field_key not in instance.attrs:
                instance.attrs[self.field_key] = {}
            return instance.attrs[self.field_key]

    def __set__(self, instance, value):
        if not isinstance(value, dict):
            raise InvalidError('`DictField` must assign a `dict` value')
        instance.attrs[self.field_key] = {}


class BaseMeta(type):
    def __init__(cls, cls_name, cls_bases, cls_dict):
        #cls = type.__new__(meta_cls, cls_name, cls_bases, cls_dict)
        for field_key, field in cls_dict.items():
            if isinstance(field, Field):
                field._register(cls, field_key)


class Base(object):
    __metaclass__ = BaseMeta
    _config = {}

    @classmethod
    def get_one(cls, _id=None):
        raw = db[cls._table].find_one({'_id': _id})
        return cls(raw)

    @classmethod
    def find(self, query={}):
        """find instance by query
        """
        cursor = db[cls._table].find(query)
        for row in cursor:
            yield cls(raw)

    @classmethod
    def _create(cls, payload):
        result = db[cls._table].insert_one(payload)
        if not result.inserted_id:
            raise Exception('create instance fail.')
        return result.inserted_id

    @classmethod
    def create(cls, payload={}):
        payload['_id'] = cls._create(payload)
        return cls(payload)

    @classmethod
    def update(cls, _id, payload={}):
        if not payload:
            return True
        result = db[cls._table].update_one({'_id': _id}, {
            '$set': payload
        })
        if result.matched_count == 1:
            return True
        else:
            return False

    def __init__(self, attrs={}):
        self.attrs = attrs

    def is_new(self):
        if '_id' in self.attrs:
            return False
        return True

    def get_id(self):
        return self.attrs['_id']

    def save(self, allow_fields=None):
        cls = type(self)
        payload = {}

        fields = set(self._config.keys())
        if allow_fields:
            fields = allow_fields & fields

        for k in fields:
            if self.is_new() and isinstance(self._config[k], IDField):
                pass  # pass if primary_key
            if k in self.attrs:
                payload[k] = self.attrs[k]

        if self.is_new():
            self.attrs['_id'] = cls.create(payload)
        else:
            cls.update(self.get_id(), payload)

    def to_dict(self):
        return self.attrs


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

    gifts = ListField()
    groups = ListField()
    events = ListField()
    relations = ListField()  # {rel: 'parent', _id: '1231212'}

    note = StringField()

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
