# -*- coding: utf-8 -*-
from collections import namedtuple
import app.error as error

from passlib.hash import pbkdf2_sha256

from app.db import db
from . import Base
from . import IDField, StringField, DateField, BoolField, ListField, TupleField


class Admin(Base):
    _table = 'admins'
    _primary_key = 'admin_id'

    admin_id = IDField(raw_field_key='_id')
    enabled = BoolField()

    @classmethod
    def login(cls, _id, password):
        raw = db[cls._table].find_one({'_id': _id}, {'_id': 1, 'password': 1, 'enabled': 1})
        if raw and raw.get('enabled', False):
            return cls.valid_password(password, raw['password'])
        return False

    @classmethod
    def hash_password(cls, password):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        return pbkdf2_sha256.encrypt(password, rounds=10 ** 5, salt_size=16)

    @classmethod
    def valid_password(cls, password, encoded):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        return pbkdf2_sha256.verify(password, encoded)

    def update_password(self, password):
        result = db[self._table].update_one({'_id': self.get_id()}, {
            '$set': {'password': self.hash_password(password)}
        })
        if result.matched_count:
            return True
        raise error.InvalidError('update password fail')


class Person(Base):
    _table = 'persons'
    _primary_key = 'person_id'

    person_id = IDField(raw_field_key='_id')
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
    relations = ListField()  # {rel: 'parent', person_id: '1231212'}
    #TupleField(namedtuple('Relation', ('rel', 'person_id')), {'rel':None, 'person_id':None})

    note = StringField()

    def get_relations(self):
        rows = {row['_id']: row for row in self.relations}
        persons, total = Person.fetch({'_id': {'$in': rows.keys()}})
        for p in persons:
            if p._id in rows:
                rows[p._id]['person'] = p
        return rows.values()
        # return Person.fetch({'_id': {'$in': _ids}})

    def build_relation(self, rel, other_person_id, due=False):
        item = {'rel': rel, 'person_id': other_person_id}
        other_person_ids = [item['person_id'] for item in self.relations]
        if other_person_id in other_person_ids:
            raise error.InvalidError('relation is existed.')

        else:
            self.relations.append(item)
            self.save(allow_fields=('relations',))
            if due:
                other_person = type(self).get_one(other_person_id)
                other_person.build_relation(rel, self.get_id())

        return True


class Group(Base):
    _table = 'groups'
    _primary_key = '_id'

    _id = IDField()
    name = StringField()
    note = StringField()
