import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from werkzeug.local import LocalProxy
from app.config import config
from app.models import Base

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



