# -*- coding: utf-8 -*-

import os
import sys
import sqlalchemy as alch
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../db/db.sqlite'))
engine = alch.create_engine('sqlite:///%s' % db_path, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


class Person(Base):
    __tablename__ = 'person'
    id = alch.Column(alch.Integer, primary_key=True)
    name = alch.Column(alch.String)


def to_dict(instance):
    return {c.name: str(getattr(instance, c.name)) for c in instance.__table__.columns}

#class Department(Base):
#    __tablename__ = 'department'
#    id = alch.Column(alch.Integer, primary_key=True)
#    name = alch.Column(alch.String)

#class Employee(Base):
#    __tablename__ = 'employee'
#    id = alch.Column(alch.Integer, primary_key=True)
#    name = alch.Column(alch.String)
#    hired_on = alch.Column(alch.DateTime, default=alch.func.now())
#    department_id = alch.Column(alch.Integer, alch.ForeignKey('department.id'))
#    department = relationship(
#        Department,
#        backref=backref('employees',
#                        uselist=True,
#                        cascade='delete,all'))
