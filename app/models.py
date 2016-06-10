import os, sys

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from app.config import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String)
    password = Column(String)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = hashlib.sha1(password).hexdigest()

    def __repr__(self):
        return "User('%s','%s', '%s')" % \
        (self.name, self.username, self.password)


def init():
    print config['DB_PATH']
    engine = create_engine('sqlite:///%s' % config['DB_PATH'], echo=True)
    Base.metadata.create_all(engine)
