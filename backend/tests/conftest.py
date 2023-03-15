import pytest

from backend import create_app


@pytest.fixture(scope='session')
def app():
    app = create_app({'TESTING': True})

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
