import dotenv
import flask_migrate
import pytest

from backend import create_app
from backend.model import db as db_


@pytest.fixture(scope='session', autouse=True)
def load_dotenv():
    dotenv.load_dotenv()


@pytest.fixture(scope='session')
def app():
    app = create_app({'TESTING': True})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        engine = db_.engine
        session = db_.session

        with engine.connect() as connection:
            transaction = connection.begin()
            engine.connect, connect = lambda: connection, engine.connect
            connection.close, close = lambda: None, connection.close
            session.commit, commit = session.flush, session.commit
            flask_migrate.upgrade()
            yield db_
            transaction.rollback()
            engine.connect = connect
            connection.close = close
            session.commit = commit


@pytest.fixture(autouse=True)
def db_session(app, db):
    session = db.session

    with session.begin_nested() as transaction:
        yield session
        transaction.rollback()
