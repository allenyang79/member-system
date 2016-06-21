# -*- coding: utf-8 -*-

import json
import sys

from flask import Flask, g
from flask import request, jsonify



import app.config as config
import app.utils as utils
import app.auth as auth

from app.error import InvalidError
from app.auth import AuthManager
from app.view import blueprint
from app.models.models import Admin

class CustomFlask(Flask):
    def make_response(self, rv):
        if isinstance(rv, (dict, list)):
            rv = json.dumps(rv, cls=self.json_encoder)
        elif isinstance(rv, tuple) and isinstance(rv[0], (list, dict)):
            rv = (json.dumps(rv[0], cls=self.json_encoder),) + rv[1:]
            #(None,) * (len(rv)-1)

        return super(CustomFlask, self).make_response(rv)

def main():
    config.load_config()

    main_app = CustomFlask(__name__)
    main_app.config.update(config.config)

    main_app.json_encoder = utils.BSONJSONEncoder
    main_app.json_decoder = utils.BSONJSONDecoder
    main_app.url_map.converters['ObjectId'] = utils.ObjectIdConverter

    am = auth.init_auth(main_app)

    main_app.register_blueprint(blueprint)

    ###############################################
    #   CORS OPTIONS request fix
    ###############################################


    @main_app.before_request
    def option_autoreply():
        if request.method == 'OPTIONS':
            resp = current_main_app.make_default_options_response()
            h = resp.headers
            # Allow the origin which made the XHR
            h['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            # Allow Credentials
            h['Access-Control-Allow-Credentials'] = 'true'
            # Allow the actual method
            h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
            # Allow for cache $n seconds
            h['Access-Control-Max-Age'] = 3600 if config.config["MODE"] == "production" else 1
            # We also keep current headers
            if 'Access-Control-Request-Headers' in request.headers:
                h['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '')
            return resp

    @main_app.after_request
    def allow_origin(response):
        if request.method == 'OPTIONS':
            return response

        response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '')
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response.headers['Access-Control-Max-Age'] = 1728000
        return response


    @main_app.errorhandler(InvalidError)
    def handle_invalid_error(error):
        return error.to_dict(), error.status_code


    @main_app.route('/')
    @main_app.route('/index')
    @am.add_whitelist
    def index():
        return {
            'success': True,
        }


    @main_app.route('/login', methods=['POST'])
    @am.add_whitelist
    def login():
        payload = request.json
        if Admin.login(payload['username'], payload['password']):
            resp = am.login(payload['username'])
            resp.data = json.dumps({'success': True, 'message': 'login success'})
            return resp
        return {'success': False, 'message': 'login fail'}, 403


    @main_app.route('/user/me')
    def user_me():
        #me = g.me
        return {
            'success': True,
            'data': auth.me().to_dict()
        }

    @main_app.route('/error')
    @am.add_whitelist
    def rasie_error():
        raise InvalidError('error', 400)

    return main_app


if __name__ == '__main__':
    main_app = main()
    main_app.run(debug=True)
