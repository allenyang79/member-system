import os
import sys

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from werkzeug.local import LocalProxy
from app.config import config


# sqlalchemy.DATE
Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'

    id = Column(sqlalchemy.Integer, primary_key=True)

    social_id = Column(sqlalchemy.String)
    name = Column(sqlalchemy.String)
    phone_0 = Column(sqlalchemy.String)
    phone_1 = Column(sqlalchemy.String)
    phone_2 = Column(sqlalchemy.String)

    address_0 = Column(sqlalchemy.String)
    address_1 = Column(sqlalchemy.String)

    email = Column(sqlalchemy.String)

    birthday = Column(sqlalchemy.Date)

    register_date = Column(sqlalchemy.Date)
    unregister_date = Column(sqlalchemy.Date)

    baptize_date = Column(sqlalchemy.Date)
    baptize_priest = Column(sqlalchemy.String)

    parent_church = Column(sqlalchemy.String)

    note = Column(sqlalchemy.String)

    # def __init__(self, name, username, password):
    #    self.name = name
    #    self.username = username
    #    self.password = hashlib.sha1(password).hexdigest()

    def __repr__(self):
        return "User('%s', '%s')" % \
            (self.id, self.name)


class PersonRelation(Base):
    __tablename__ = 'person_relations'
    id = Column(sqlalchemy.Integer, sqlalchemy.Sequence('person_relations_seq'), primary_key=True)
    from_id = Column(sqlalchemy.Integer, ForeignKey('persons.id'))
    to_id = Column(sqlalchemy.Integer, ForeignKey('persons.id'))
    rel = Column(sqlalchemy.String)
    __table_args__ = (
        sqlalchemy.UniqueConstraint('from_id', 'to_id', name='_from_id_to_id'),
    )


class PersonEvent(Base):
    __tablename__ = 'person_events'

    id = Column(sqlalchemy.Integer, sqlalchemy.Sequence('person_events_seq'), primary_key=True)
    person_id = Column(sqlalchemy.Integer, ForeignKey('persons.id'))
    person = relationship("Person", backref="person_events")
    date = Column(sqlalchemy.Date)
    title = Column(sqlalchemy.String)


def init():
    global _engine, _session
    echo = True if config['MODE'] == 'development' else False
    _engine = create_engine('sqlite:///%s' % config['DB_PATH'], echo=echo)
    Base.metadata.create_all(_engine)

    Session = sessionmaker(bind=engine)
    _session = Session()


def find_engine():
    if _engine is None:
        raise Exception('models has not init')
    else:
        return _engine


def find_session():
    if _session is None:
        raise Exception('models has not init')
    else:
        return _session

_engine = None
engine = LocalProxy(find_engine)

_session = None
session = LocalProxy(find_session)
