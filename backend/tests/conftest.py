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

from tests.auth import admin_session, role, user_session  # noqa: F401
from backend import create_app
from backend.model import db as db_


@pytest.fixture(scope='session', autouse=True)
def load_dotenv() -> None:
    dotenv.load_dotenv()


@pytest.fixture(scope='session')
def app() -> collections.abc.Generator[Flask, None, None]:
    app = create_app({
        'TESTING': 'True',
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
        engine = db_.engine
        session = db_.session

        with engine.connect() as connection:
            transaction = connection.begin()
            engine.connect, connect = (  # type: ignore
                lambda: connection,
                engine.connect,
            )
            connection.close, close = (  # type: ignore
                lambda: None,
                connection.close,
            )
            session.commit, commit = (  # type: ignore
                session.flush,
                session.commit,
            )
            flask_migrate.upgrade()
            yield db_
            transaction.rollback()
            engine.connect = connect  # type: ignore
            connection.close = close  # type: ignore
            session.commit = commit  # type: ignore


@pytest.fixture(autouse=True)
def db_session(app: Flask, db: SQLAlchemy) -> collections.abc.Generator[
    scoped_session[Session],
    None,
    None,
]:
    session = db.session

    with session.begin_nested() as transaction:
        yield session
        transaction.rollback()
