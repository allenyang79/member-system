# -*- coding: utf-8 -*-
import os
import sys
import unittest

from app.config import config
from app.models import session
from app.models import Person
from app.models import PersonEvent


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sample(self):
        p0 = Person(name='allen', phone_0='0988')
        session.add(p0)
        session.commit()

        p1 = Person(name='bill', phone_0='0988')
        session.add(p1)
        session.commit()

        pe = PersonEvent(person=p0, title='hello')
        session.add(pe)
        session.commit()

        print p0.person_events

        row = session.query(Person).filter_by(name='bill').first()
        self.assertEqual(row.name, 'bill')
        #db_path = os.path.join(os.path.dirname(__file__),'db/user.json')
        #user_db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))
        #user_db.insert({'type': 'apple', 'count': 7})
