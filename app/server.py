# -*- coding: utf-8 -*-

import json
import sys
import re

from flask import Flask
from flask import request, jsonify

from app.error import InvalidError
from app import utils
from app.models.models import Person, Group


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


######################
#   Person
######################


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


@app.route('/person/<_id>/relation', methods=['POST'])
def person_build_relation(_id):
    payload = request.json
    if 'rel' not in payload or 'person_id' not in payload:
        raise InvalidError('`rel` and `person_id` should in payload.')

    person = Person.get_one(_id)
    if not person:
        raise InvalidError('Person(%s) is not existed.' % _id)

    person.build_relation(payload['rel'], payload['person_id'], due=True)
    return {'success': True}


@app.route('/person/list')
def person_list():
    term = str(request.values.get('term', ''))
    group = str(request.values.get('group', ''))
    #limit = int(request.values.get('limit', 0))
    #offset = int(request.values.get('offset', 0))

    query = {}
    if term:
        query['name'] = {'$regex': re.escape(term), '$options': 'i'}

    if group:
        pass
        #query['name'] = {'$regex': re.escape(term), '$options': 'i'}

    result = Person.fetch(query)
    data = []
    for person in result:
        data.append(person.to_dict())

    return {
        'success': True,
        'data': data,
    }


@app.route('/person/create', methods=['POST'])
def person_create():
    payload = request.json
    p = Person.create(payload)

    return {
        'success': True,
        'data': p.to_dict()
    }

######################
#   group
######################


@app.route('/group/create', methods=['POST'])
def group_create():
    payload = request.json
    group = Group.create(payload)
    return {
        'success': True,
        'data': group.to_dict()
    }


@app.route('/group/one/<_id>/update', methods=['POST'])
def group_one_update(_id):
    group = Group.get_one(_id)
    if not group:
        raise InvalidError('Group(%s) is not existed.' % _id)

    payload = request.json
    group.update(payload)
    group.save()

    return {
        'success': True,
        'data': group.to_dict()
    }


@app.route('/group/one/<_id>')
def group_one(_id):
    group = Group.get_one(_id)
    return {
        'success': True,
        'data': group.to_dict()
    }


@app.route('/group/list')
def group_list():
    result = Group.fetch()
    data = []
    for group in result:
        data.append(group.to_dict())

    return {
        'success': True,
        'data': data,
    }


if __name__ == '__main__':
    app.run(debug=True)
