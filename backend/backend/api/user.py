from typing import Any, cast

from flask import abort, jsonify, request
from flask.typing import ResponseReturnValue
from flask_marshmallow_openapi import open_api
from marshmallow import Schema, fields

from backend.model import db
from backend.model.user import Role, User
from backend.schema import CreateSchema, EmptySchema
from backend.schema.user import UserSchema
from . import api
from .auth import auth


@open_api.post(UserSchema, CreateSchema)
@api.post('/users')
@auth.login_required(role=Role.ADMINISTRATOR)
def create_user() -> ResponseReturnValue:
    user = UserSchema(exclude=['id', 'creation_date']).load(request.json)

    User.check_duplicate(user)

    db.session.add(user)
    db.session.commit()

    user.send_created_email()
    return {'id': str(user.id)}, 201


@open_api.post(EmptySchema)
@api.post('/users/<user:user>/send-created-email')
@auth.login_required(role=Role.ADMINISTRATOR)
def send_user_created_email(user: User) -> ResponseReturnValue:
    user.send_created_email()
    return '', 204


@api.put('/users/<user:user>')
@auth.login_required(role=Role.ADMINISTRATOR)
def update_user(user: User) -> ResponseReturnValue:
    UserSchema(exclude=['id', 'creation_date', 'email']).load(
        request.json,
        instance=user,
        partial=True,
    )
    db.session.commit()
    return jsonify(UserSchema().dump(user))


@open_api.get_list(UserSchema)
@api.get('/users')
@auth.login_required(role=Role.ADMINISTRATOR)
def list_users() -> ResponseReturnValue:
    users = User.query.order_by(User.creation_date)
    return {'users': UserSchema(many=True).dump(users)}


@open_api.get(UserSchema)
@api.get('/users/<user:user>')
@auth.login_required(role=Role.ADMINISTRATOR)
def get_user(user: User) -> ResponseReturnValue:
    return jsonify(UserSchema().dump(user))


@open_api.get(EmptySchema, operation_id='get_password_state')
@api.get('/set-password/<token>')
def get_password_state(token: str) -> ResponseReturnValue:
    user = User.from_password_token(token)

    if not user:
        abort(404, 'user_not_found')

    if user.password:
        abort(409, 'password_already_set')

    return '', 204


class PasswordSchema(Schema):
    password = fields.Str()


@open_api.post(
    request_schema=PasswordSchema,
    response_schema=EmptySchema,
    operation_id='set_password',
)
@api.post('/set-password/<token>')
def set_password(token: str) -> ResponseReturnValue:
    password = PasswordSchema().load(
        cast(dict[str, Any], request.json)
    )['password']
    user = User.from_password_token(token)

    if not user:
        abort(404, 'user_not_found')

    if user.password:
        abort(409, 'password_already_set')

    user.set_password(password)
    db.session.commit()
    return '', 204


@open_api.get(EmptySchema)
@api.get('/reset-password/<email>')
def send_reset_password_email(email: str) -> ResponseReturnValue:
    user = User.from_email(email)

    if not user:
        abort(404, 'user_not_found')

    user.send_reset_password_email()
    return '', 204


@open_api.post(
    request_schema=PasswordSchema,
    response_schema=EmptySchema,
    operation_id='reset_password',
)
@api.post('/reset-password/<token>')
def reset_password(token: str) -> ResponseReturnValue:
    password = PasswordSchema().load(
        cast(dict[str, Any], request.json)
    )['password']
    user = User.from_password_token(token)

    if not user:
        abort(404, 'user_not_found')

    user.set_password(password)
    db.session.commit()
    return '', 204


@api.delete('/users/<user:user>')
@auth.login_required(role=Role.ADMINISTRATOR)
def delete_user(user: User) -> ResponseReturnValue:
    db.session.delete(user)
    db.session.commit()
    return '', 204
