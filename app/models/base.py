# -*- coding: utf-8 -*-

import copy
import functools
import os
import sys
import weakref
import datetime
import bson
import logging
from collections import namedtuple

from app.error import InvalidError
from app.db import db


logger = logging.getLogger()

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

    def __init__(self, raw_field_key=None, **kw):
        """
        :param str raw_field_key:
        :param default: value or function

        """
        self.raw_field_key = raw_field_key

        if 'default' in kw:
            self.default = kw['default']

    def __get__(self, instance, cls):
        if not instance:
            return self
        else:
            if self.raw_field_key not in instance._attrs:
                if hasattr(self, 'default'):
                   # if has `default`, then use this `default` to generate value
                   if hasattr(self.default, '__call__'):
                       instance._attrs[self.raw_field_key] = self.value_in(instance, self.default())
                   else:
                       instance._attrs[self.raw_field_key] = self.value_in(instance, self.default)
                else:
                    return None
            return self.value_out(instance, instance._attrs[self.raw_field_key])

    def __set__(self, instance, value):
        """ set value to instance's field.

        TODO: how to handle none value???

        """
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

    def value_in(self, instance, value):
        """The value from external to instance._attrs"""
        return value

    def value_out(self, instance, value):
        """ The value from instance._attrs to external"""
        return value

    def encode(self, instance, target):
        """ Encode external value to another data type that json.dumps can process. """
        if self.raw_field_key in instance._attrs:
            target[self.field_key] = getattr(instance, self.field_key)

    def decode(self, instance, payload):
        """ decode external value from another data type that json.loads can process. """
        if self.field_key in payload:
            value = payload[self.field_key]
            setattr(instance, self.field_key, value)



class IDField(Field):
    def __init__(self, raw_field_key='_id', **kw):
        if 'default' not in kw:
            kw['default'] = lambda: str(bson.ObjectId())
        kw['raw_field_key'] = raw_field_key
        super(IDField, self).__init__(**kw)


class StringField(Field):
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = ''
        super(StringField, self).__init__(**kw)

    def value_in(self, instance, value):
        return str(value)

    def value_out(self, instance, value):
        return value


class BoolField(Field):
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = False
        super(BoolField, self).__init__(**kw)

    def value_in(self, instance, value):
        return bool(value)

    def value_out(self, instance, value):
        return value


class IntField(Field):
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = 0
        super(IntField, self).__init__(**kw)

    def value_in(self, instance, value):
        return int(value)

    def value_out(self, instance, value):
        return value


class DateField(Field):
    def __init__(self, **kw):
        """ DateField
            :param datetime default: default can be like ex: lamda: datetime.date.today()
        """
        # if 'default' not in kw:
        #    kw['default'] = datetime.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
        super(DateField, self).__init__(**kw)

    def value_in(self, instance, value):
        if isinstance(value, datetime.date):
            return datetime.datetime.combine(value, datetime.datetime.min.time())
        elif isinstance(value, datetime.datetime):
            return value.replace(minute=0, hour=0, second=0, microsecond=0)
        raise ModelInvaldError('`DateField` only accept `date` value, not `%s`' % repr(value))

    def value_out(self, instance, value):
        return value.date()

    def encode(self, instance, target):
        if self.raw_field_key in instance._attrs:
            target[self.field_key] = getattr(instance, self.field_key).strftime('%Y-%m-%d')

    def decode(self, instance, payload):
        if self.field_key in payload:
            try:
                value = datetime.datetime.strptime(payload[self.field_key], '%Y-%m-%d').date()
                setattr(instance, self.field_key, value)
            except Exception as e:
                logger.warning(e)
                logger.warning('can not decode `%s` `%s`', self.field_key, payload[self.field_key])



class ListField(Field):
    def __init__(self, **kw):
        """ ListField.
        """
        if 'default' not in kw:
            kw['default'] = lambda: []
        super(ListField, self).__init__(**kw)

    def value_in(self, instance, value):
        return list(value)


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

    def encode(self, instance, target):
        if self.raw_field_key in instance._attrs:
            target[self.field_key] = getattr(instance, self.field_key).__dict__

    def decode(self, instance, payload):
        if self.field_key in payload:
            try:
                value = self.np(**payload[self.field_key])
                setattr(instance, self.field_key, value)
            except Exception as e:
                logger.warning(e)
                logger.warning('can not decode `%s` `%s`', self.field_key, payload[self.field_key])


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
    def fetch(cls, query={}, sort=None, offset=None, limit=None):
        cursor = cls._find(query)
        return FetchResult(cls, cursor)

    @classmethod
    def create(cls, payload={}):
        for field_key, field in cls._config.iteritems():
            if field_key not in payload:
                if hasattr(field, 'default'):
                    if hasattr(field.default, '__call__'):
                        payload[field_key] = field.default()
                    else:
                        payload[field_key] = field.default
        instance = cls(payload)
        instance.save()
        return instance

    def __init__(self, payload={}):
        """ Do not use Foo() to create new instance.
        instate cls.create or cls.get_one() is better.
        """
        for field_key, value in payload.items():
            if field_key in self._config:
                setattr(self, field_key, value)
            else:
                raise ModelError('create a `%s` instance with unfield key, value (%s, %s).' % (type(self).__name__, field_key, value))

        # self._attrs.update(_attrs)
        # for k, v in values.items():
        #    if k not in self._config:
        #        raise ModelError('create a `%s` instance with unfield key,value (%s, %s).' % (type(self), k, v))
        #    setattr(self, k, v)

    def is_new(self):
        #primary_field = self._config[self._primary_key]
        # if primary_field.raw_field_key not in self._attrs:
        #    return True
        if db[self._table].find_one({'_id': self.get_id()}, ('_id')):
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
            payload['_id'] = self._attrs[primary_field.raw_field_key]
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
            field.encode(self, result)
        return result


    def update_from_jsonify(self, payload, allow_fields=None):
        """update a value from external dict by json.loads()."""
        for field_key, field in self._config.iteritems():
            field.decode(self, payload)
        return self

    @classmethod
    def from_jsonify(cls, payload):
        if '__class__' in payload and payload['__class__'] == cls.__name__:
            instance = cls({})
            for field_key, field in cls._config.iteritems():
                field.decode(instance, payload)
            return instance
        raise ModelParserError('can not parse `%s` to `%s` instance.' % (payload, cls.__name__))
