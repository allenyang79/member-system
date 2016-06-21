# -*- coding: utf-8 -*-
import json
import sys
import time
import traceback

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
        endpoint = flask.request.url_rule.endpoint if hasattr(flask.request, 'url_rule') and hasattr(flask.request.url_rule, 'endpoint') else None

        if not endpoint:
            pass
        elif endpoint in self.whitelist:
            pass
        elif self.auth():
            pass


    def login(self, username, exp=None):
        """
        payload = {
            'username': 'username',
            'exp': '(Expiration Time) Claim',
            'nbf': '(Not Before Time) Claim',
            'iss': '(Issuer) Claim',
            'aud': '(Audience) Claim',
            'iat': '(Issued At) Claim',
        }
        """
        #if 'exp' not in payload:
        #    payload['exp'] = int(time.time()) +
        if exp is None:
            exp = self.app.config.get('JWT_EXPIRE_TIME', 86400)

        payload = {
            'username': username,
            'exp': int(time.time()) + exp
        }

        if not payload:
            raise LoginFailError('Login fail.')

        token = jwt.encode(payload, self.app.config['JWT_SECRET'], algorithm='HS256')
        resp = flask.make_response()
        resp.set_cookie('jwt', token, expires=payload['exp'])
        return resp

    def logout(self):
        flask.request.set_cookie('jwt', None, expires=0)
        return True

    def auth(self, silence=False):
        try:
            encoded = flask.request.cookies.get('jwt')
            if not encoded:
                raise UnauthorizedError('no token')
            payload = jwt.decode(encoded, self.app.config['JWT_SECRET'], algorithms=['HS256'])
            if int(time.time()) > payload['exp'] > int(time.time()):
                raise UnauthorizedError('expire time')

            username = payload['username']
            if getattr(self, '_load_user') and hasattr(self._load_user, '__call__'):
                flask.g.me = self._load_user(username)
            return True

        except UnauthorizedError as e:
            if not silence:
                raise e
        except jwt.exceptions.DecodeError as e:
            if not silence :
                raise UnauthorizedError('token decode fail')
        return False

    #jwt.encode({'exp': 1371720939}, 'secret')
    def add_whitelist(self, rule):
        self.whitelist.append(rule.func_name)
        return rule


    def load_user(self, fn):
        self._load_user = fn


def me(silence=False):
    if flask.has_request_context():
        if hasattr(flask.g, 'me'):
            return flask.g.me

    if not silence:
        raise UnauthorizedError('user has not login.')

    return None

def init_auth(app):
    am = AuthManager(app)

    @am.load_user
    def load_user(_id):
        user = Admin.get_one(_id)
        return user

    return am
