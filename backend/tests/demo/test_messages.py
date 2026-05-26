from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Self

import gevent
import gevent.queue
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session

from backend.demo import messages as messages_module
from backend.demo.model.message import Message
from backend.model import db
from backend.model.user import User


def test_messages_stream(
    test_client: FlaskClient,
    admin_session: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        messages_module,
        'listener_greenlet',
        SimpleNamespace(dead=False),
    )

    response = test_client.get('/messages')
    assert response.status_code == 200
    response_iterator = response.iter_encoded()

    # Ignore existing messages
    for _ in Message.query:
        next(response_iterator)

    assert next(response_iterator) == b':heartbeat\n'
    response = test_client.post('/messages', json={'text': 'Some text'})
    message_id = response.get_json()['id']
    data = json.loads(next(response_iterator).decode()[len('data: '):])
    assert data['id'] == message_id
    assert data['text'] == 'Some text'


def test_messages_post_invalid(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    before_count = Message.query.count()

    response = test_client.post('/messages')
    assert response.status_code == 400
    assert response.json == {'message': 'expected_json'}
    assert Message.query.count() == before_count

    response = test_client.post('/messages', json={'not_text': 'Some text'})
    assert response.status_code == 400
    assert response.json == {'not_text': ['Unknown field.']}
    assert Message.query.count() == before_count


def test_messages_post_empty(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    before_count = Message.query.count()

    response = test_client.post('/messages', json={'text': ''})
    assert response.status_code == 400
    assert response.json == {'text': ['Shorter than minimum length 1.']}
    assert Message.query.count() == before_count


def test_messages_post_valid(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    before_count = Message.query.count()

    response = test_client.get('/messages')
    response_iterator = response.iter_encoded()

    # Ignore existing messages
    for _ in Message.query:
        next(response_iterator)

    response = test_client.post('/messages', json={'text': 'Some text'})
    assert Message.query.count() == before_count + 1
    last_message = Message.query.order_by(Message.date.desc()).first()
    assert last_message
    assert last_message.text == 'Some text'
    assert response.status_code == 201
    assert response.json == {'id': str(last_message.id)}

    assert next(response_iterator) == b':heartbeat\n'
    data = json.loads(next(response_iterator).decode()[len('data: '):])
    assert data['id'] == str(last_message.id)
    assert data['text'] == 'Some text'


def test_messages_post_assigns_author_for_regular_user(
    test_client: FlaskClient,
    user_session: None,
    user: User,
    db_session: scoped_session[Session],
) -> None:
    response = test_client.post('/messages', json={'text': 'User message'})
    assert response.status_code == 201

    message_id = response.get_json()['id']
    message = db_session.get(Message, message_id)
    assert message
    assert message.author
    assert message.author.id == user.id


def test_messages_delete_valid(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    before_count = Message.query.count()
    response = test_client.post('/messages', json={'text': 'Some text'})
    message_id = response.get_json()['id']
    assert Message.query.count() == before_count + 1

    response = test_client.delete(f'/messages/{message_id}')
    assert response.status_code == 204
    assert response.data == b''
    assert Message.query.count() == before_count


def test_messages_delete_missing(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    response = test_client.delete(
        '/messages/00000000-0000-0000-0000-000000000000'
    )
    assert response.status_code == 404
    assert response.get_json() == {'message': 'message_not_found'}


def test_trigger_message_notifications(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executed: list[tuple[str, dict[str, str]]] = []

    class Transaction:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def execute(self, statement: object, params: dict[str, str]) -> None:
            executed.append((str(statement), params))

    monkeypatch.setattr(
        db.engine,
        'begin',
        lambda: Transaction(),
    )

    session = SimpleNamespace(
        info={messages_module.SESSION_MESSAGES_CHANGED_KEY: True},
    )
    messages_module.trigger_message_notifications(session)

    assert session.info == {}
    assert executed == [(
        'SELECT pg_notify(:channel, :payload)',
        {'channel': messages_module.MESSAGES_CHANNEL, 'payload': ''},
    )]


def test_listen_notifications(
    app: Flask,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    full_queue: gevent.queue.Queue[None] = gevent.queue.Queue(maxsize=1)
    full_queue.put_nowait(None)
    ready_queue: gevent.queue.Queue[None] = gevent.queue.Queue(maxsize=1)
    monkeypatch.setattr(
        messages_module,
        'subscriber_queues',
        {full_queue, ready_queue},
    )

    class Connection:
        def __init__(self) -> None:
            self.notifies = [object()]
            self.statement = ''
            self.closed = False
            self.committed = False

        def cursor(self) -> Connection:
            return self

        def execute(self, sql: str) -> None:
            self.statement = sql

        def commit(self) -> None:
            self.committed = True

        def poll(self) -> None:
            return None

        def close(self) -> None:
            self.closed = True

    connection = Connection()
    monkeypatch.setattr(
        db.engine,
        'raw_connection',
        lambda: connection,
    )

    logged: list[str] = []

    def stop_loop(_: float) -> None:
        raise RuntimeError('stop')

    with app.app_context():
        monkeypatch.setattr(gevent, 'sleep', stop_loop)
        monkeypatch.setattr(app.logger, 'exception', logged.append)
        messages_module.listen_notifications()

    assert connection.statement == (
        f'LISTEN {messages_module.MESSAGES_CHANNEL};'
    )
    assert connection.committed is True
    assert connection.closed is True
    assert full_queue.qsize() == 1
    assert ready_queue.qsize() == 1
    assert logged == ['Message notification listener stopped']
    assert messages_module.listener_greenlet is None
