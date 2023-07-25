from flask import Blueprint, Request, current_app, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import BadRequest, NotFound

api = Blueprint('api', __name__)
auth = HTTPBasicAuth(scheme='BasicAPI')
error_messages = {
    401: 'unauthorized',
    403: 'forbidden',
}


def raise_expected_json(request, error):
    raise BadRequest('expected_json')


Request.on_json_loading_failed = raise_expected_json


@api.errorhandler(BadRequest)
@api.errorhandler(NotFound)
def bad_request(error):
    return {'message': error.description}, error.code


@auth.error_handler
def error_handler(status_code):
    return {
        'message': error_messages.get(status_code, 'unknown_error')
    }, status_code


@auth.verify_password
def verify_password(username, password):
    if session.get('admin'):
        return 'admin'

    admin_password = current_app.config['ADMIN_PASSWORD']

    if (
        username == 'admin'
        and password == admin_password
    ):
        session['admin'] = True
        return 'admin'


from . import admin, messages  # noqa: F401, E402
