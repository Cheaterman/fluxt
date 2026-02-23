from typing import NoReturn, Self

from flask import Blueprint, request, session
from flask import Request as FlaskRequest
from flask.blueprints import BlueprintSetupState
from flask.typing import ResponseReturnValue
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound

api = Blueprint('api', __name__)

from backend.model.file import FileConverter  # noqa: E402
from backend.model.superadmin import SuperAdmin  # noqa: E402
from backend.model.user import Role, User, UserConverter  # noqa: E402

from .auth import Authable, auth  # noqa: E402

error_messages = {
    401: 'unauthorized',
    403: 'forbidden',
}


class Request(FlaskRequest):
    def on_json_loading_failed(self: Self, e: ValueError | None) -> NoReturn:
        raise BadRequest('expected_json')


@api.record_once
def register_url_converters(state: BlueprintSetupState) -> None:
    state.app.url_map.converters['file'] = FileConverter
    state.app.url_map.converters['user'] = UserConverter


def raise_expected_json(request: Request, error: BadRequest) -> BadRequest:
    raise BadRequest('expected_json')


@api.errorhandler(BadRequest)
@api.errorhandler(Conflict)
@api.errorhandler(Forbidden)  # Business logic 403, not RBAC
@api.errorhandler(NotFound)
def http_error(
    error: BadRequest | Conflict | Forbidden | NotFound,
) -> ResponseReturnValue:
    assert error.code
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
    user = (
        SuperAdmin.auth(username, password)
        or User.auth(username, password)
    )

    if username and password and user:
        # Successful fresh login, evaluate & apply remember me status
        remember_me = {
            'true': True,
            'false': False,
        }.get(request.headers.get('Fluxt-Remember-Me', 'false'), False)
        session.permanent = remember_me

    return user


@auth.get_user_roles
def get_user_roles(user: Authable) -> list[Role]:
    return [user.get_role()]


from . import file as _file  # noqa: F401, E402
from . import user as _user  # noqa: F401, E402
