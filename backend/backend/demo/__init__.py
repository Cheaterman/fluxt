from flask import Blueprint, Request
from flask.blueprints import BlueprintSetupState
from flask.typing import ResponseReturnValue
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound

from .model.message import MessageConverter

api = Blueprint('demo', __name__)


@api.record_once
def register_url_converters(state: BlueprintSetupState) -> None:
    state.app.url_map.converters['message'] = MessageConverter


def raise_expected_json(request: Request, error: BadRequest) -> BadRequest:
    raise BadRequest('expected_json')


setattr(Request, 'on_json_loading_failed', raise_expected_json)


@api.errorhandler(BadRequest)
@api.errorhandler(Conflict)
@api.errorhandler(Forbidden)  # Business logic 403, not RBAC
@api.errorhandler(NotFound)
def http_error(
    error: BadRequest | Conflict | Forbidden | NotFound,
) -> ResponseReturnValue:
    return {'message': error.description}, error.code


@api.errorhandler(ValidationError)
def validation_error(error: ValidationError) -> ResponseReturnValue:
    return error.messages_dict, 400


from . import (  # noqa: F401, E402
    messages,
)
