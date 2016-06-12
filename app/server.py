# -*- coding: utf-8 -*-

import json
import sys
import bson

from flask import Flask
from flask import request, jsonify

from app.error import InvalidError
from app.models import Person
from app.models import Group
from app import utils


class CustomFlask(Flask):
    def make_response(self, rv):
        if isinstance(rv, (dict, list)):
            rv = jsonify(rv)
        return super(CustomFlask, self).make_response(rv)

app = CustomFlask(__name__)
app.json_encoder = utils.BSONJSONEncoder
app.json_decoder = utils.BSONJSONDecoder
app.url_map.converters['ObjectId'] = utils.ObjectIdConverter


@app.errorhandler(InvalidError)
def handle_invalid_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
@app.route('/index')
def index():
    return {
        'success': True
    }


@app.route('/person/one/<_id>')
def person_one(_id):
    person = Person.get_one(_id)
    return {
        'success': True,
        'data': person.to_dict()
    }


@app.route('/person/one/<_id>/update', methods=['POST'])
def person_one_update(_id):
    person = Person.get_one(_id)
    if not person:
        raise InvalidError('Person(%s) is not existed.' % _id)

    payload = request.json
    for field in (
            'name',
            'phone_0',
            'phone_1',
            'phone_2',
            'address_0',
            'address_1',
            'email_0',
            'email_1',
            'education',
            'job',
            'birthday',
            'register_day',
            'unregister_day',
            'baptize_date',
            'baptize_priest',
            'gifts',
            'groups',
            'events',
            'note'
        ):
        if field in payload:
            setattr(person, field, payload[field])
    person.save()
    return {
        'success': True,
        'data': person.to_dict()
    }


@app.route('/person/build_relation', methods=['POST'])
def person_build_relation():
    post = request.json
    if not ('rel' in post and 'p1' in post and 'p2' in post):
        return {
            'message': 'args now allow',
            'success': False
        }

    Person.build_relation(post['rel'], post['p1'], post['p2'])
    return {
        'success': True,
    }


@app.route('/person/list')
def person_list():
    term = str(request.values.get('term'))
    limit = int(request.values.get('limit', 0))
    return {
        'success': True,
        'data': data,
        'meta': {
            'total': 0,
            'offset': 0,
            'limit': 10
        }
    }


@app.route('/person/create', methods=['POST'])
def person_create():
    payload = request.json
    p = Person.create(payload)

    return {
        'success': True,
        'data': p.to_dict()
    }


if __name__ == '__main__':
    app.run(debug=True)
