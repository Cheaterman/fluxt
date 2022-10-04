import pytest

from backend import app


@pytest.fixture(scope='session')
def app_context():
    with app.app_context():
        yield app


@pytest.fixture
def client(app_context):
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client
