from __future__ import annotations

import typing

from flask import Blueprint, session
from flask.typing import ResponseReturnValue
from flask_httpauth import HTTPBasicAuth
from flask_marshmallow_openapi import open_api
from marshmallow import Schema, fields

from backend import api as api_module
from backend.model.user import Role
from backend.schema import EmptySchema


api = typing.cast(Blueprint, api_module.api)  # type: ignore
auth = HTTPBasicAuth(scheme='BasicAPI')


class AuthInfo(typing.TypedDict):
    id: str
    email: str
    role: Role
    first_name: str
    last_name: str


class Authable(typing.Protocol):
    @classmethod
    def auth(cls, username: str, password: str) -> Authable | None: ...

    def get_role(self) -> Role: ...

    def get_auth_info(self) -> AuthInfo: ...


class AuthSchema(Schema):
    id = fields.String()
    email = fields.String()
    role = fields.String()
    first_name = fields.String()
    last_name = fields.String()


@open_api.get(AuthSchema, operation_id='auth')
@api.get('/auth')
@auth.login_required
def authenticate() -> ResponseReturnValue:
    return typing.cast(Authable, auth.current_user()).get_auth_info()


@open_api.get(EmptySchema, operation_id='deauth')
@api.get('/deauth')
def deauthenticate() -> ResponseReturnValue:
    session.clear()
    return '', 204
