# -*- coding: utf-8 -*-
import os
import sys
import json
import unittest
import bson

from app.config import config
from app.server import app as main_app
from app.db import db
from app.models.models import Person
from app.models.models import Group


class TestServer(unittest.TestCase):
    def setUp(self):
        main_app.debug = True
        self.client = main_app.test_client()

    def tearDown(self):
        db.persons.delete_many({})
        db.groups.delete_many({})

    def test_heartbeat(self):
        r = self.client.get('/')
        # print r
        # print r.data
        self.assertEqual(json.loads(r.data), {
            'success': True
        })

    def test_person_create_update(self):
        return
        post = {
            'name': 'Bill',
            'phone_0': '0988'
        }
        r = self.client.post('/person/create', data=json.dumps(post), content_type='application/json')
        self.assertEqual(r.status_code, 200)

        person_id = json.loads(r.data)['data']['_id']

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

        return


    def test_person_build_relation(self):
        return
        db.persons.insert_many([{
            '_id': 'p1',
            'name': 'Bill'
        },{
            '_id': 'p2',
            'name': 'John'
        }])
        post = {
            'rel' : 'family',
            'p1': 'p1',
            'p2': 'p2'
        }
        r = self.client.post('/person/build_relation', data=json.dumps(post), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        return

    def test_person_list(self):
        return
        r = self.client.get('/person/list')
        self.assertEqual(r.status_code, 200)

    def test_person_one(self):
        return
        r = self.client.get('/person/one/%s' % person_id)
        self.assertEqual(r.status_code, 200)



