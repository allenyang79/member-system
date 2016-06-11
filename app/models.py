import os
import sys
import weakref

from app.db import db


class Field(object):
    def __init__(self):
        pass

    def __get__(self, instance, cls):
        if instance and self.field_key in instance.attrs:
            return instance.attrs[self.field_key]
        else:
            return None

    def __set__(self, instance, value):
        #self.values[instance] = value
        instance.attrs[self.field_key] = value

    def register(self, cls, field_key):
        self.field_key = field_key
        cls._config[field_key] = {}


class IDField(Field):
    def register(self, cls, field_key):
        self.field_key = field_key
        cls._config[field_key] = {
            'primary_key': True
        }


class BaseMeta(type):
    def __init__(cls, cls_name, cls_bases, cls_dict):
        #cls = type.__new__(meta_cls, cls_name, cls_bases, cls_dict)
        for field_key, field in cls_dict.items():
            if isinstance(field, Field):
                field.register(cls, field_key)


class Base(object):
    __metaclass__ = BaseMeta
    _config = {}

    @classmethod
    def find(self, query):
        for raw in db[cls._table].find(query):
            yield cls(raw)

    @classmethod
    def get_one(cls, _id=None):
        raw = db[cls._table].find_one({'_id': _id})
        return cls(raw)

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

    def save(self):

        cls = type(self)
        payload = {}
        # process payload
        for k in self._config:
            if 'primary_key' in self._config[k] and self.is_new():
                pass
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
    # register_field('name')
    _id = IDField()

    social_id = Field()
    name = Field()
    phone_0 = Field()
    phone_1 = Field()
    phone_2 = Field()

    address_0 = Field()
    address_1 = Field()

    email_0 = Field()
    email_1 = Field()

    education = Field()
    job = Field()

    register_date = Field()
    unregister_date = Field()

    baptize_date = Field()
    baptize_priest = Field()

    gifts = Field()
    groups = Field()
    events = Field()

    note = Field()
    relations = Field()
    #{rel: 'parent', _id: '1231212'}


class Group(Base):
    _table = 'groups'

    _id = IDField()
    name = Field()
