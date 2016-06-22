# -*- coding: utf-8 -*-

import Cookie
import os
import sys
import json
import unittest
import bson

import werkzeug.http
import jwt

import app.server as server
from app.config import config
from app.db import db
from app.error import InvalidError
from app.auth import UnauthorizedError, LoginFailError
from app.models.models import Admin

import mock


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.main_app = server.main()
        cls.main_app.debug = True

    def setUp(self):
        self.client = self.main_app.test_client()

    def tearDown(self):
        db.persons.delete_many({})
        db.groups.delete_many({})

    def test_unauthorized_error(self):
        """Test UnauthorizedError is a InvalidError."""
        err = UnauthorizedError("unauthorized.")
        self.assertIsInstance(err, InvalidError)

        err = LoginFailError("login fail.")
        self.assertIsInstance(err, InvalidError)

    def test_heartbeat(self):
        """Test heartbeat."""
        r = self.client.get('/')
        self.assertEqual(json.loads(r.data), {
            'success': True
        })

        r = self.client.get('/index')
        self.assertEqual(json.loads(r.data), {
            'success': True
        })

    def test_auth(self):
        """Test auth."""
        db.admins.insert_many([{
            '_id': 'admin',
            'password': Admin.hash_password('1234'),
            'enabled': True
        }])

        post = {
            'username': 'admin',
            'password': '1234'
        }
        r = self.client.post('/login', data=json.dumps(post), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        cookies = r.headers.getlist('Set-Cookie')
        encoded = None
        for cookie in cookies:
            key, value = werkzeug.http.parse_cookie(cookie).items()[0]
            if key == 'jwt':
                encoded = value

        payload = jwt.decode(encoded, self.main_app.config['JWT_SECRET'], algorithms=['HS256'])
        self.assertEqual(payload['username'], 'admin')

        r = self.client.get('/user/me')
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.data)['data']
        self.assertEqual(result['_id'], 'admin')

    def test_unauth(self):
        """Test unauth."""
        return

        r = self.client.get('/user/me')
        self.assertEqual(r.status_code, 403)

    def test_raise_error(self):
        """Test raise error."""
        return

        r = self.client.get('/error')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(json.loads(r.data), {'success': False, 'message': 'error'})
