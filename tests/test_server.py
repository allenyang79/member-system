# -*- coding: utf-8 -*-

import os
import sys
import json
import unittest
import bson

from app.config import config
from app.server import main
from app.db import db
from app.models.models import Person
from app.models.models import Group


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.main_app = main()
        self.main_app.debug = True
        self.client = self.main_app.test_client()

    def tearDown(self):
        db.persons.delete_many({})
        db.groups.delete_many({})

    def test_person_create_update(self):
        """/person/create"""
        post = {
            'name': 'Bill',
            'phone_0': '0988'
        }
        r = self.client.post('/person/create', data=json.dumps(post), content_type='application/json')
        self.assertEqual(r.status_code, 200)

        person_id = json.loads(r.data)['data']['person_id']
        r = self.client.get('/person/one/%s' % person_id)
        self.assertEqual(r.status_code, 200)

        _person = json.loads(r.data)['data']
        self.assertEqual(_person['name'], post['name'])
        self.assertEqual(_person['phone_0'], post['phone_0'])

        post = {
            'phone_1': 'phine_1_update',
            'address_0': 'address_0_update'
        }
        r = self.client.post('/person/one/%s/update' % person_id, data=json.dumps(post), content_type='application/json')
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/person/one/%s' % person_id)
        self.assertEqual(r.status_code, 200)

        _person = json.loads(r.data)['data']
        self.assertEqual(_person['phone_1'], post['phone_1'])
        self.assertEqual(_person['address_0'], post['address_0'])


    def test_person_build_relation(self):
        """/person/<_id>/relation"""
        db.persons.insert_many([{
            '_id': 'id_0',
            'name': 'Bill'
        }, {
            '_id': 'id_1',
            'name': 'John'
        }])
        post = {
            'rel': 'family',
            'person_id': 'id_1'
        }
        r = self.client.post('/person/id_0/relation', data=json.dumps(post), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        for row in db.persons.find():
            if row['_id'] == 'id_0':
                self.assertIn({'rel': 'family', 'person_id': 'id_1'}, row['relations'])

            if row['_id'] == 'id_1':
                self.assertIn({'rel': 'family', 'person_id': 'id_0'}, row['relations'])

        r = self.client.post('/person/id_0/relation', data=json.dumps(post), content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_person_list(self):
        """/person/list"""
        db.persons.insert_many([{
            '_id': 'id_1',
            'name': 'Bill'
        }, {
            '_id': 'id_2',
            'name': 'John'
        }, {
            '_id': 'id_3',
            'name': 'Mary',
        }])

        r = self.client.get('/person/list')
        self.assertEqual(r.status_code, 200)

        result = json.loads(r.data)['data']
        for row in result:
            if row['person_id'] == 'id_1':
                self.assertEqual(row['name'], 'Bill')
            elif row['person_id'] == 'id_2':
                self.assertEqual(row['name'], 'John')
            elif row['person_id'] == 'id_3':
                self.assertEqual(row['name'], 'Mary')

        r = self.client.get('/person/list?term=john')
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.data)['data']
        self.assertEqual(result[0]['name'], 'John')

    def test_person_one(self):
        """/person/one/<_id>"""
        db.persons.insert_many([{
            '_id': 'id_1',
            'name': 'Bill'
        }, {
            '_id': 'id_2',
            'name': 'John'
        }])
        r = self.client.get('/person/one/id_1')
        self.assertEqual(r.status_code, 200)

        result = json.loads(r.data)['data']
        self.assertEqual(result['person_id'], 'id_1')
        self.assertEqual(result['name'], 'Bill')

    def test_group(self):
        """/group/create"""
        payload = {
            'name': 'group-1',
            'note': 'this is note'
        }
        r = self.client.post('/group/create', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.data)['data']
        group_id = result['_id']

        _group = db.groups.find_one({'_id': group_id})
        self.assertEqual(_group['name'], payload['name'])
        self.assertEqual(_group['note'], payload['note'])

        payload = {
            'name': 'group-1-update',
        }
        r = self.client.post('/group/one/%s/update' % group_id, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.data)['data']

        _group = db.groups.find_one({'_id': result['_id']})
        self.assertEqual(_group['name'], payload['name'])

    def test_group_list(self):
        """/group/list"""
        db.groups.insert_many([{
            '_id': 'id_0',
            'name': 'group-0'
        }, {
            '_id': 'id_1',
            'name': 'group-1'
        }])
        r = self.client.get('/group/list')
        result = json.loads(r.data)['data']
        for row in result:
            if row['_id'] == 'id_0':
                self.assertEqual(row['name'], 'group-0')
            elif row['_id'] == 'id_1':
                self.assertEqual(row['name'], 'group-1')

        r = self.client.get('/group/one/id_1')
        result = json.loads(r.data)['data']
        self.assertEqual(result['name'], 'group-1')
