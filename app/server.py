# -*- coding: utf-8 -*-

import json
import sys

from flask import Flask
from flask import request, jsonify

from app.config import load_config, config
from app import utils
from app.error import InvalidError
from app.view import blueprint

class CustomFlask(Flask):
    def make_response(self, rv):
        if isinstance(rv, (dict, list)):
            rv = jsonify(rv)
        return super(CustomFlask, self).make_response(rv)


app = CustomFlask(__name__)
app.json_encoder = utils.BSONJSONEncoder
app.json_decoder = utils.BSONJSONDecoder
app.url_map.converters['ObjectId'] = utils.ObjectIdConverter


app.register_blueprint(blueprint)

###############################################
#   CORS OPTIONS request fix
###############################################


@app.before_request
def option_autoreply():
    if request.method == 'OPTIONS':
        resp = current_app.make_default_options_response()
        h = resp.headers
        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        # Allow Credentials
        h['Access-Control-Allow-Credentials'] = 'true'
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for cache $n seconds
        h['Access-Control-Max-Age'] = 3600 if config["MODE"] == "production" else 1
        # We also keep current headers
        if 'Access-Control-Request-Headers' in request.headers:
            h['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '')
        return resp

@app.after_request
def allow_origin(response):
    if request.method == 'OPTIONS':
        return response

    response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '')
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Max-Age'] = 1728000
    return response


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

"""
from flask_jwt import jwt_required, current_identity
from app.auth import MyJWT,authenticate, identity
app.config['SECRET_KEY'] = 'super-secret'
jwt = MyJWT(app, authenticate, identity)

@app.route('/admin')
@jwt_required
def admin():
    return '%s' % current_identity
"""


if __name__ == '__main__':
    load_config()
    app.config.update(config)
    app.run(debug=True)
