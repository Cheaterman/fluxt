import pytest
from flask import session

from backend import create_app, ConfigurationError
from backend.model import Message


@pytest.fixture
def admin_password(app):
    return app.config['ADMIN_PASSWORD']


@pytest.fixture
def admin_session(client):
    with client.session_transaction() as session:
        session['admin'] = True


@pytest.fixture
def message(db):
    message = Message(text='Test message')
    db.session.add(message)
    db.session.flush()
    return message


def test_config_missing_password():
    with pytest.raises(ConfigurationError):
        create_app({'ADMIN_PASSWORD': ''})


def test_no_credentials(client):
    response = client.get('/auth')
    assert response.status_code == 401
    assert response.get_json()['message'] == 'unauthorized'


def test_invalid_username(client, admin_password):
    response = client.get('/auth', auth=('invalid_username', admin_password))
    assert response.status_code == 401
    assert response.get_json()['message'] == 'unauthorized'


def test_invalid_password(client):
    response = client.get('/auth', auth=('admin', 'invalid_password'))
    assert response.status_code == 401
    assert response.get_json()['message'] == 'unauthorized'


def test_valid(client, admin_password):
    with client:
        client.get('/auth')  # Create session
        assert 'admin' not in session
        response = client.get('/auth', auth=('admin', admin_password))
        assert response.status_code == 200
        assert response.data == b''
        assert session.get('admin') is True


def test_cookie(client, admin_session):
    response = client.get('/auth')
    assert response.status_code == 200
    assert response.data == b''


def test_message_delete_invalid_id(client, admin_session):
    response = client.delete('/messages/0')
    assert response.status_code == 404
    assert response.get_json()['message'] == 'invalid_message_id'


def test_message_delete_valid(client, admin_session, message, db):
    assert db.session.get(Message, message.id) is message
    response = client.delete(f'/messages/{message.id}')
    assert response.status_code == 204
    assert response.data == b''
    assert db.session.get(Message, message.id) is None
