import collections.abc
import os

import dotenv
import flask_migrate
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session

from backend import create_app
from backend.model import db as db_
from tests.auth import admin_session, role, user_session  # noqa: F401


@pytest.fixture(scope='session', autouse=True)
def load_dotenv() -> None:
    dotenv.load_dotenv()


@pytest.fixture(scope='session')
def app() -> collections.abc.Generator[Flask, None, None]:
    app = create_app({
        'TESTING': 'True',
        'STREAM_REFRESH_INTERVAL': 0,
        # Needed for redirecting to Nuxt
        'APPLICATION_ROOT': os.environ.get('SCRIPT_NAME', '/api/'),
        'EMAIL_HOST': 'localhost',
        'EMAIL_USE_TLS': '',
        'EMAIL_USE_SSL': '',
    })
    yield app


@pytest.fixture
def test_client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope='session')
def db(app: Flask) -> collections.abc.Generator[SQLAlchemy, None, None]:
    with app.app_context():
        # See https://github.com/sqlalchemy/sqlalchemy/issues/11163
        engine = db_.engine
        connection = engine.connect()
        transaction = connection.begin()
        # pylint: disable=protected-access
        db_.session = db_._make_scoped_session({
            'bind': connection,
            'join_transaction_mode': 'create_savepoint',
        })
        # XXX: Maybe we can avoid monkeypatching here somehow
        db_.session.commit = db_.session.flush  # type: ignore
        flask_migrate.upgrade()
        try:
            yield db_
        finally:
            transaction.rollback()


@pytest.fixture(autouse=True)
def db_session(app: Flask, db: SQLAlchemy) -> collections.abc.Generator[
    scoped_session[Session],
    None,
    None,
]:
    session = db.session

    with session.begin_nested() as transaction:
        try:
            yield session
        finally:
            transaction.rollback()
