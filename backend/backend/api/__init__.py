from flask import Blueprint, Request
from werkzeug.exceptions import BadRequest

api = Blueprint('api', __name__)


def raise_expected_json(request, error):
    raise BadRequest('expected_json')


Request.on_json_loading_failed = raise_expected_json


@api.errorhandler(BadRequest)
def bad_request(error):
    return {'message': error.description}, error.code


from . import messages  # noqa: F401, E402
