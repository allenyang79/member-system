# -*- coding: utf-8 -*-

from . import Base
from . import IDField, StringField, DateField, ListField

class Person(Base):
    _table = 'persons'
    _primary_key = '_id'

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
        rows = {row['_id']: row for row in self.relations}
        persons, total = Person.fetch({'_id': {'$in': rows.keys()}})
        for p in persons:
            if p._id in rows:
                rows[p._id]['person'] = p
        return rows.values()

        #return Person.fetch({'_id': {'$in': _ids}})

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
    _primary_key = '_id'

    _id = IDField()
    name = StringField()
    note = StringField()
