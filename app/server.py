# -*- coding: utf-8 -*-

import json
import sys

from flask import Flask
from flask import current_app, g
from flask import request, jsonify

import app.config as config
import app.utils as utils
import app.auth as auth

from app.logger import logger

from app.error import InvalidError
from app.auth import AuthManager
from app.view import blueprint
from app.models.models import Admin


class CustomFlask(Flask):
    def make_response(self, rv):
        if isinstance(rv, (dict, list)):
            return super(CustomFlask, self).make_response((json.dumps(rv, cls=self.json_encoder), 200, {
                'Content-type': 'application/json; charset=utf-8'
            }))
        elif isinstance(rv, tuple) and isinstance(rv[0], (list, dict)):
            resp = super(CustomFlask, self).make_response((json.dumps(rv[0], cls=self.json_encoder),) + rv[1:])
            resp.headers['Content-type'] = 'application/json; charset=utf-8'
            return resp

        return super(CustomFlask, self).make_response(rv)


def main():
    logger.info("main start")
    config.load_config()

    main_app = CustomFlask(__name__)
    main_app.config.update(config.config)

    main_app.json_encoder = utils.BSONJSONEncoder
    main_app.json_decoder = utils.BSONJSONDecoder
    main_app.url_map.converters['ObjectId'] = utils.ObjectIdConverter

    am = auth.init_auth(main_app)

    main_app.register_blueprint(blueprint)

    # init admin
    admin = Admin.get_one('admin')
    if not admin:
        admin = Admin.create({
            'admin_id': config.config['DEFAULT_ADMIN_USERNAME'],
            'enabled': True,
        })
        admin.update_password(config.config['DEFAULT_ADMIN_PASSWORD'])

    ###############################################
    #   CORS OPTIONS request fix
    ###############################################

    @main_app.before_request
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
        logger.error(error)
        if config.config['MODE'] == 'production':
            if isinstance(error, auth.UnauthorizedError):
                return {'success': False, 'message': 'Unauthorized.'}, error.status_code
            elif isinstance(error, auth.LoginFailError):
                return {'success': False, 'message': 'Login fail.'}, error.status_code
        return error.to_dict(), error.status_code

    @main_app.route('/')
    @main_app.route('/index')
    def index():
        return {
            'success': True,
        }

    @main_app.route('/login', methods=['POST'])
    def login():
        payload = request.json

        username = str(payload.get('username', '')).strip()
        password = str(payload.get('password', '')).strip()
        if not username or not password:
            return {'success': False, 'message': 'login fail'}, 403

        if Admin.login(username, password):
            resp = am.login_user({'username': username})

            resp.data = json.dumps({
                'success': True,
                'message': 'login success',
                'data': am.me().to_jsonify()
            })
            return resp
        return {'success': False, 'message': 'login fail'}, 403

    @main_app.route('/logout')
    def logout():
        resp = am.logout_user()
        resp.data = json.dumps({
            'success': True,
            'message': 'logout success',
            'data': None
        })
        return resp


    @main_app.route('/user/me')
    @am.login_required
    def user_me():
        #me = g.me
        return {
            'success': True,
            'data': am.me().to_jsonify()
        }

    @main_app.route('/error')
    def rasie_error():
        raise InvalidError('error', 400)

    return main_app


if __name__ == '__main__':
    main_app = main()
    main_app.run(debug=True)
