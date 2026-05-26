from __future__ import annotations

import datetime
from collections.abc import Generator
from typing import cast

import gevent
import gevent.queue
from flask import Response, current_app, request, stream_with_context
from flask.typing import ResponseReturnValue
from marshmallow import Schema, fields
from marshmallow.validate import Length
from sqlalchemy import event, select, text
from sqlalchemy.orm import Session

from backend.api.auth import auth
from backend.model import db
from backend.model.superadmin import SuperAdmin
from backend.model.user import Role, User

from . import api
from .model.message import Message

MESSAGES_CHANNEL = 'messages'
SESSION_MESSAGES_CHANGED_KEY = 'messages_changed'
subscriber_queues: set[gevent.queue.Queue[None]] = set()
listener_greenlet: gevent.Greenlet[[], None] | None = None


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


def notify_subscribers() -> None:
    for subscriber_queue in tuple(subscriber_queues):
        try:
            subscriber_queue.put_nowait(None)
        except gevent.queue.Full:
            continue


def ensure_listener_running() -> None:
    global listener_greenlet

    if listener_greenlet and not listener_greenlet.dead:
        return

    listener_greenlet = gevent.spawn(listen_notifications)


def listen_notifications() -> None:
    global listener_greenlet

    connection = db.engine.raw_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(f'LISTEN {MESSAGES_CHANNEL};')
        connection.commit()

        while True:
            connection.poll()

            while connection.notifies:
                connection.notifies.pop(0)
                notify_subscribers()

            gevent.sleep(0.1)

    except Exception:
        current_app.logger.exception('Message notification listener stopped')

    finally:
        listener_greenlet = None
        connection.close()


def notify_messages() -> None:
    with db.engine.begin() as connection:
        connection.execute(
            text('SELECT pg_notify(:channel, :payload)'),
            {'channel': MESSAGES_CHANNEL, 'payload': ''},
        )


@event.listens_for(Session, 'after_flush')
def mark_messages_changed(session: Session, _: object) -> None:
    for changed_entity in (
        session.new | session.dirty | session.deleted
    ):
        if isinstance(changed_entity, Message):
            session.info[SESSION_MESSAGES_CHANGED_KEY] = True
            return


@event.listens_for(Session, 'after_commit')
def trigger_message_notifications(session: Session) -> None:
    messages_changed = session.info.pop(SESSION_MESSAGES_CHANGED_KEY, False)

    if messages_changed:
        notify_messages()


@event.listens_for(Session, 'after_rollback')
def clear_message_notifications(session: Session) -> None:
    session.info.pop(SESSION_MESSAGES_CHANGED_KEY, None)


@api.get('/messages')
@auth.login_required
def messages_stream() -> ResponseReturnValue:
    ensure_listener_running()
    schema = MessageSchema()

    def stream() -> Generator[str, None, None]:
        last_date = datetime.datetime.min.replace(tzinfo=datetime.UTC)
        subscriber_queue: gevent.queue.Queue[None] = gevent.queue.Queue(
            maxsize=1
        )
        subscriber_queues.add(subscriber_queue)

        stream_refresh_interval = current_app.config['STREAM_REFRESH_INTERVAL']

        try:
            while True:
                for message in db.session.scalars(
                    select(Message)
                    .where(Message.date > last_date)
                    .order_by(Message.date)
                ):
                    yield f'data: {schema.dumps(message)}\n\n'
                    last_date = message.date

                try:
                    subscriber_queue.get(timeout=stream_refresh_interval)

                except gevent.queue.Empty:
                    yield ':heartbeat\n'

        finally:
            subscriber_queues.discard(subscriber_queue)

    return Response(
        stream_with_context(stream()),
        mimetype='text/event-stream',
    )


class CreateMessageSchema(Schema):
    text = fields.String(validate=Length(min=1))


@api.post('/messages')
@auth.login_required
def messages_add() -> ResponseReturnValue:
    data = cast(dict[str, str], CreateMessageSchema().load(request.json))

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
