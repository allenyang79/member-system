# -*- coding: utf-8 -*-
import json
import sys

from flask import Flask
from flask import request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

from app.error import InvalidError
from app.models.models import Admin



def authenticate(_id, password):
    admin = Admin.get_one(_id)
    if admin and safe_str_cmp(admin.password.encode('utf-8'), password.encode('utf-8')):
        return admin


def identity(payload):
    user_id = payload['identity']
    admin = Admin.get_one(_id)
    return admin


class MyJWT(JWT):
    pass

