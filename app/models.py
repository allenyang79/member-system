import os, sys

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from werkzeug.local import LocalProxy


from app.config import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    address = Column(String)

    #def __init__(self, name, username, password):
    #    self.name = name
    #    self.username = username
    #    self.password = hashlib.sha1(password).hexdigest()

    def __repr__(self):
        return "User('%s', '%s', '%s', '%s')" % \
        (self.id, self.name, self.phone, self.address)


def init():
    print "====init===="
    global _engine, _session
    _engine = create_engine('sqlite:///%s' % config['DB_PATH'], echo=True)
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
