# -*- coding: utf-8 -*-

import os
import sys

from flask import Flask
from flask_graphql import GraphQLView

from models import db_session
from models import Base, engine

from schema import schema

Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.debug = True

# This is creating the `/graphql` and `/graphiql` endpoints
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    return 'index'


@app.route('/init')
def init():
    # db init
    from models import Person
    allen = Person(name='allen')
    db_session.add(allen)
    db_session.commit()
    """
    from models import Department, Employee

    engineering = Department(name='Engineering')
    db_session.add(engineering)

    hr = Department(name='Human Resources')
    db_session.add(hr)

    peter = Employee(name='Peter', department=engineering)
    db_session.add(peter)
    roy = Employee(name='Roy', department=engineering)
    db_session.add(roy)
    tracy = Employee(name='Tracy', department=hr)
    db_session.add(tracy)
    db_session.commit()
    """
    return "done"



if __name__ == '__main__':
    app.run()
