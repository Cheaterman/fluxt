import datetime
from typing import Any, Generator, cast

import gevent
from flask import Response, current_app, request, stream_with_context
from flask.typing import ResponseReturnValue
from marshmallow import Schema, fields
from marshmallow.validate import Length
from sqlalchemy import select

from backend.api.auth import auth
from backend.model import db
from backend.model.superadmin import SuperAdmin
from backend.model.user import Role, User
from .model.message import Message
from . import api


def serialize_author(message: Message) -> str:
    author = message.author

    if not author:
        return 'Admin'

    return f'{author.first_name} {author.last_name}'


class MessageSchema(Schema):
    id = fields.String()
    date = fields.DateTime()
    author = fields.Function(serialize=serialize_author)
    text = fields.String()


@api.get('/messages')
@auth.login_required
def messages_stream() -> ResponseReturnValue:
    schema = MessageSchema()

    def stream() -> Generator[str, None, None]:
        last_date = datetime.datetime.min

        while True:
            for message in db.session.scalars(
                select(Message)
                .where(Message.date > last_date)
                .order_by(Message.date)
            ):
                yield f'data: {schema.dumps(message)}\n\n'
                last_date = message.date

            gevent.sleep(current_app.config['STREAM_REFRESH_INTERVAL'])
            yield ':heartbeat\n'

    return Response(
        stream_with_context(stream()),
        mimetype='text/event-stream',
    )


class CreateMessageSchema(Schema):
    text = fields.String(validate=Length(min=1))


@api.post('/messages')
@auth.login_required
def messages_add() -> ResponseReturnValue:
    data = CreateMessageSchema().load(
        cast(dict[str, Any], request.json)
    )

    message = Message()
    message.text = data['text']
    user = cast(User | SuperAdmin, auth.current_user())

    if user.email != 'admin':
        message.author = cast(User, user)

    db.session.add(message)
    db.session.commit()

    return {'id': str(message.id)}, 201


@api.delete('/messages/<message:message>')
@auth.login_required(role=Role.ADMINISTRATOR)
def messages_delete(message: Message) -> ResponseReturnValue:
    db.session.delete(message)
    db.session.commit()

    return '', 204
