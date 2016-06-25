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


class ModelSaveError(InvalidError):
    """Base model operator error."""
    pass


class Field(object):
    """Decalre a propery for Model"""
    field_key = None
    raw_field_key = None

    def __init__(self, raw_field_key=None, default_value=None, allow_none=True, allow_encode=True):
        """
        :param str raw_field_key:
        :param str default_value:
        :param bool allow_none:
        :param bool allow_encode: it will not encode on instance.to_dict

        """
        self.raw_field_key = raw_field_key
        self.default_value = default_value
        self.allow_none = allow_none
        self.allow_encode = allow_encode

    def __get__(self, instance, cls):
        if instance:
            if self.raw_field_key not in instance._attrs:
                instance._attrs[self.raw_field_key] = self.value_default(instance)
            if instance._attrs[self.raw_field_key] is None:
                return None
            return self.value_out(instance, instance._attrs[self.raw_field_key])
        return self

    def __set__(self, instance, value):
        if value is None:
            instance._attrs[self.raw_field_key] = None
        else:
            instance._attrs[self.raw_field_key] = self.value_in(instance, value)

    def register(self, cls, field_key):
        """ Bind the property name with model cls.
            When declare complete. this function will call by Model's Meta. and bind by the property name.
        """
        self.field_key = field_key
        if self.raw_field_key is None:
            self.raw_field_key = field_key
        cls._config[field_key] = self

    # process value in/out of db
    def value_default(self, instance):
        """ The default value of this field."""
        return self.default_value

    def value_in(self, instance, value):
        """The value from external to instance._attrs"""
        return value

    def value_out(self, instance, value):
        """ The value from instance._attrs to external"""
        return value

    def encode(self, instance):
        """ Encode external value to another data type that json.dumps can process. """
        if hasattr(instance, self.field_key):
            return getattr(instance, self.field_key)  # _attrs[self.raw_field_key]
        return None

    def decode(self, payload):
        """ decode external value from another data type that json.loads can process. """
        if self.field_key in payload:
            return payload[self.field_key]
        else:
            return None


class IDField(Field):
    def __init__(self, raw_field_key='_id', allow_none=False, **kw):
        kw['raw_field_key'] = raw_field_key
        kw['allow_none'] = allow_none
        super(IDField, self).__init__(**kw)

    def generate_id(self, instance):
        return str(bson.ObjectId())


class StringField(Field):
    def __init__(self, **kw):
        if 'default_value' not in kw:
            kw['default_value'] = ''
        super(StringField, self).__init__(**kw)

    def value_in(self, instance, value):
        return str(value)

    def value_out(self, instance, value):
        return value


class BoolField(Field):
    def __init__(self, **kw):
        if 'default_value' not in kw:
            kw['default_value'] = False
        super(BoolField, self).__init__(**kw)

    def value_in(self, instance, value):
        return bool(value)

    def value_out(self, instance, value):
        return value


class IntField(Field):
    def __init__(self, **kw):
        if 'default_value' not in kw:
            kw['default_value'] = 0
        super(IntField, self).__init__(**kw)

    def value_in(self, instance, value):
        return int(value)

    def value_out(self, instance, value):
        return value


class DateField(Field):
    def __init__(self, **kw):
        """ DateField
            :param datetime default_value: default is datetime.datetime(1900, 1, 1).replace(minute=0, hour=0, second=0, microsecond=0)
        """
        if 'default_value' not in kw:
            kw['default_value'] = datetime.datetime(1900, 1, 1).replace(minute=0, hour=0, second=0, microsecond=0)
        super(DateField, self).__init__(**kw)

    def value_in(self, instance, value):
        if isinstance(value, datetime.date):
            return datetime.datetime.combine(value, datetime.datetime.min.time())
        elif isinstance(value, datetime.datetime):
            return value.replace(minute=0, hour=0, second=0, microsecond=0)
        raise ModelInvaldError('`DateField` only accept `date` value, not `%s`' % repr(value))

    def value_out(self, instance, value):
        return value.date()

    def encode(self, instance):
        if hasattr(instance, self.field_key):
            #print self.field_key, getattr(instance, self.field_key)
            val = getattr(instance, self.field_key)
            if val:
                return val.strftime('%Y-%m-%d')
        return None

    def decode(self, payload):
        if self.field_key in payload:
            return datetime.datetime.strptime(payload[self.field_key], '%Y-%m-%d')
        return None


class ListField(Field):
    def __init__(self, **kw):
        """ ListField.
        """
        if 'default_value' in kw:
            raise ModelDeclareError('ListField\'s default_value show overwrite on value_default method')
        super(ListField, self).__init__(**kw)

    def value_in(self, instance, value):
        return list(value)

    def value_default(self, instance):
        """ Return a new list for default."""
        return []


class TupleField(Field):

    def __init__(self, np, **kw):
        """ TupleField.
            :param namedtuple np: ex: namedtuple('Point', ['x', 'y'], verbose=True)
        """
        if not np:
            raise ModelDeclareError('Declare a tuple field without namedtuple `np`.')
        super(TupleField, self).__init__(**kw)
        self.np = np

    def value_in(self, instance, value):
        return value.__dict__

    def value_out(self, instance, value):
        if isinstance(value, dict):
            return self.np(**value)
        return None

    def encode(self, instance):
        if hasattr(instance, self.field_key):
            return getattr(instance, self.field_key).__dict__
        return None

    def decode(self, payload):
        if self.field_key in payload:
            return self.np(**payload[self.field_key])
        return None


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
    def __new__(meta_cls, cls_name, cls_bases, cls_dict):
        cls = type.__new__(meta_cls, cls_name, cls_bases, cls_dict)
        if cls_name == 'Base':
            return cls
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
        return cls


class FetchResult(object):
    def __init__(self, cls, cursor):
        self.cls = cls
        self.root_cursor = cursor
        self.cursor = self.root_cursor.clone()

    def __iter__(self):
        return self

    def __getitem__(self, key):
        return self.cls.get_one(raw=self.cursor[key])

    def next(self):
        return self.cls.get_one(raw=next(self.cursor))

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
    def get_one(cls, _id=None, raw=None):
        if _id and raw is None:
            raw = db[cls._table].find_one({'_id': _id}, projection={field.raw_field_key: True for field in cls._config.values()})
            if not raw:
                return None
        elif raw and _id is None:
            pass
        else:
            raise ModelInvaldError('get_one arguemtn errors.')

        instance = cls({})
        instance._attrs.update(raw)
        return instance

    @classmethod
    def create(cls, payload={}):
        instance = cls(payload)
        instance.save()
        return instance

    @classmethod
    def fetch(cls, query={}, sort=None, offset=None, limit=None):
        cursor = cls._find(query)
        return FetchResult(cls, cursor)

    def __init__(self, values={}):
        # self._attrs.update(_attrs)
        for k, v in values.items():
            if k not in self._config:
                raise ModelError('create a `%s` instance with unfield key,value (%s, %s).' % (type(self), k, v))
            setattr(self, k, v)

    def is_new(self):
        primary_field = self._config[self._primary_key]
        if primary_field.raw_field_key not in self._attrs:
            return True
        elif db[self._table].find_one({'_id': self.get_id()}, ('_id')):
            return False
        return True

    def get_id(self):
        return getattr(self, self._primary_key)

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
            # if self.is_new() and isinstance(self._config[k], IDField):
            #    pass  # pass if primary_key
            if k == self._primary_key:
                continue
            elif k in self._attrs:
                payload[k] = self._attrs[k]

        if self.is_new():
            primary_field = self._config[self._primary_key]
            if getattr(self, self._primary_key):
                payload['_id'] = self._attrs[primary_field.raw_field_key]
            else:
                payload['_id'] = self._attrs[primary_field.raw_field_key] = primary_field.generate_id(self)
            if cls._insert_one(payload):
                return True

        else:
            if cls._update_one({'_id': self.get_id()}, payload):
                return True
        raise ModelSaveError('can not save instance of `%s`' % type(self))

    def to_jsonify(self):
        """ return a dict, that can be dump to json.
        """
        result = {
            '__class__': type(self).__name__
        }
        for field_key, field in self._config.iteritems():
            result[field_key] = field.encode(self)
        return result

    #def update(self, payload):
    #    """update a value from external dict by json.loads()."""
    #    for field_key, field in self._config.iteritems():
    #        setattr(self, field_key, field.decode(payload))
    #    return self

    def update_from_jsonify(self, payload, allow_fields=None):
        """update a value from external dict by json.loads()."""
        for field_key, field in self._config.iteritems():
            if allow_fields:
                if field_key in allow_fields:
                    setattr(self, field_key, field.decode(payload))
            else:
                setattr(self, field_key, field.decode(payload))
        return self

    @classmethod
    def from_jsonify(cls, payload):
        if '__class__' in payload and payload['__class__'] == cls.__name__:
            raw = {}
            for field_key, field in cls._config.iteritems():
                raw[field_key] = field.decode(payload)
            return cls(raw)
        raise ModelParserError('can not parse `%s` to `%s` instance.' % (payload, cls.__name__))
