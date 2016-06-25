# -*- coding: utf-8 -*-

import functools
import json
import os
import sys
import time
import traceback
import binascii
import flask
#from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
import jwt
import jwt.exceptions

from app.error import InvalidError
#from app.auth import AuthManager
from app.models.models import Admin


class LoginFailError(InvalidError):
    def __init__(self, message='Login fail.', status_code=403):
        super(LoginFailError, self).__init__(message, status_code)


class UnauthorizedError(InvalidError):
    def __init__(self, message='Unauthorized.', status_code=403):
        super(UnauthorizedError, self).__init__(message, status_code)


class AuthManager(object):
    """A auth plugin for flask.

    AuthManger auth the user by JWT encode/decode. and put a jwt key on cookie.
    if auth fail, it will riase UnauthorizedError or LoginFailError.
    and you can custom errorHandler on flask app to handler this type of error.

    """
    def __init__(self, app=None):
        self.app = None
        self.mode = 'deny_first'
        self.whitelist = []

        if app is not None:
            self.app = app
            self.init_app(self.app)

    def init_app(self, app):
        self.app = app
        self.app.extensions['jwt'] = self
        self.app.before_request(self.before_request)

    def before_request(self):
        if hasattr(flask.request, 'url_rule') and hasattr(flask.request.url_rule, 'endpoint'):
            endpoint = flask.request.url_rule.endpoint
        else:
            endpoint = None

        #print "==before_login on AuthManager=="
        #print self.app.view_functions.keys()
        #if not endpoint:
        #    pass
        #elif endpoint in self.whitelist:
        #    pass
        #elif self.auth():
        #    pass

    def login_user(self, payload):
        """
        .. code-block:: python

            payload = {
                ...
                'exp': '(Expiration Time) Claim',
            }
        """

        if 'exp' not in payload:
            payload['exp'] = int(time.time()) + self.app.config.get('JWT_EXPIRE_TIME', 86400)
        token = jwt.encode(payload, self.app.config['JWT_SECRET'], algorithm='HS256', headers={'salt': binascii.hexlify(os.urandom(16))})
        resp = flask.make_response()
        resp.headers['content-type'] = 'application/json; charset=utf-8'
        resp.set_cookie('jwt', token, expires=payload['exp'])


        #username = payload['username']
        if getattr(self, '_load_user') and hasattr(self._load_user, '__call__'):
            flask.g.me = self._load_user(payload)

        return resp

    def logout_user(self):
        resp = flask.make_response()
        resp.headers['content-type'] = 'application/json; charset=utf-8'
        resp.set_cookie('jwt', '', expires=0)
        return resp
        #flask.request.set_cookie('jwt', None, expires=0)
        #return True

    def auth(self):
        try:
            encoded = flask.request.cookies.get('jwt')
            if not encoded:
                return False, 'No JWT token.'

            payload = jwt.decode(encoded, self.app.config['JWT_SECRET'], algorithms=['HS256'])
            if not payload:
                return False, 'Payload is empty.'

            if int(time.time()) > payload['exp'] > int(time.time()):
                return False, 'JWT token expired.'

            #username = payload['username']
            if getattr(self, '_load_user') and hasattr(self._load_user, '__call__'):
                flask.g.me = self._load_user(payload)
            else:
                raise Exception('please implement load_user to mixin.')
            return True, None
        except jwt.exceptions.DecodeError as e:
            return False, 'Jwt deocode fail.'


    ##jwt.encode({'exp': 1371720939}, 'secret')
    # def add_whitelist(self, rule):
    #    self.whitelist.append(rule.func_name)
    #    return rule

    def load_user(self, func):
        self._load_user = func

    def login_required(self, func):
        """Wrap a endpoint function to validate before __call__.

        .. code-block:: python


            @app.route('/hello')
            @am.login_required
            def hello():
                return {}

        """
        @functools.wraps(func)
        def decorated_view(*args, **kwargs):
            if flask.request.method in ('OPTIONS'):
                return func(*args, **kwargs)

            is_auth, message = self.auth()
            if is_auth:
                return func(*args, **kwargs)
            raise UnauthorizedError(message)
            # elif current_app.login_manager._login_disabled:
            #    return func(*args, **kwargs)
            # elif not current_user.is_authenticated:
            #    return current_app.login_manager.unauthorized()
        return decorated_view


    def me(self, silence=False):
        if flask.has_request_context():
            if hasattr(flask.g, 'me'):
                return flask.g.me

        if not silence:
            raise UnauthorizedError('current user has not login.')

        return None


def init_auth(app):
    am = AuthManager(app)

    @am.load_user
    def load_user(payload):
        """Payload from jwt decode."""
        _id = payload['username']
        user = Admin.get_one(_id)
        return user

    return am
