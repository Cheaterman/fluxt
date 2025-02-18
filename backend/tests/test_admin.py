import typing

import pytest
from flask import Flask, session
from flask.testing import FlaskClient

from backend.model.user import Role


@pytest.fixture
def admin_password(app: Flask) -> str:
    return typing.cast(str, app.config['ADMIN_PASSWORD'])


def test_config_missing_password(
    test_client: FlaskClient,
    app: Flask,
    admin_password: str,
) -> None:
    app.config['ADMIN_PASSWORD'] = ''
    response = test_client.get('/auth', auth=('admin', admin_password))
    assert response.status_code == 401
    assert response.get_json()['message'] == 'unauthorized'


def test_no_credentials(test_client: FlaskClient) -> None:
    response = test_client.get('/auth')
    assert response.status_code == 401
    assert response.get_json()['message'] == 'unauthorized'


def test_invalid_username(
    test_client: FlaskClient,
    admin_password: str,
) -> None:
    response = test_client.get(
        '/auth',
        auth=('invalid_username', admin_password),
    )
    assert response.status_code == 401
    assert response.get_json()['message'] == 'unauthorized'


def test_invalid_password(test_client: FlaskClient) -> None:
    response = test_client.get('/auth', auth=('admin', 'invalid_password'))
    assert response.status_code == 401
    assert response.get_json()['message'] == 'unauthorized'


def test_valid(test_client: FlaskClient, admin_password: str) -> None:
    with test_client:
        test_client.get('/auth')  # Create session
        assert 'admin' not in session
        response = test_client.get('/auth', auth=('admin', admin_password))
        assert response.status_code == 200
        assert response.get_json() == {
            'id': '',
            'name': 'admin',
            'roles': [Role.ADMINISTRATOR.value],
        }
        assert session.get('admin') is True


def test_cookie(test_client: FlaskClient, admin_session: None) -> None:
    response = test_client.get('/auth')
    assert response.status_code == 200
    assert response.get_json() == {
        'id': '',
        'name': 'admin',
        'roles': [Role.ADMINISTRATOR.value],
    }


def test_deauth(test_client: FlaskClient, admin_session: None) -> None:
    with test_client:
        response = test_client.get('/deauth')
        assert response.status_code == 204
        assert response.data == b''
        assert 'admin' not in session
