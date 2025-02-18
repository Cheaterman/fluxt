from flask import Blueprint, Request
from flask.typing import ResponseReturnValue
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound

api = Blueprint('api', __name__)

from backend.model.admin import Admin  # noqa: E402
from backend.model.user import Role, User  # noqa: E402
from .auth import Authable, auth  # noqa: E402

error_messages = {
    401: 'unauthorized',
    403: 'forbidden',
}


def raise_expected_json(request: Request, error: BadRequest) -> BadRequest:
    raise BadRequest('expected_json')


setattr(Request, 'on_json_loading_failed', raise_expected_json)


@api.errorhandler(BadRequest)
@api.errorhandler(Conflict)
@api.errorhandler(Forbidden)  # Business logic 403, not RBAC
@api.errorhandler(NotFound)
def bad_request(
    error: BadRequest | Conflict | Forbidden | NotFound,
) -> ResponseReturnValue:
    return {'message': error.description}, error.code


@api.errorhandler(ValidationError)
def validation_error(error: ValidationError) -> ResponseReturnValue:
    return error.messages_dict, 400


@auth.error_handler
def error_handler(status_code: int) -> ResponseReturnValue:
    return {
        'message': error_messages.get(status_code, 'unknown_error'),
    }, status_code


@auth.verify_password
def verify_password(username: str, password: str) -> Authable | None:
    return (
        Admin.auth(username, password)
        or User.auth(username, password)
    )


@auth.get_user_roles
def get_user_roles(user: Authable) -> list[Role]:
    return user.get_roles()
