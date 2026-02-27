from __future__ import annotations

from typing import cast
from unittest.mock import Mock

import pytest
from flask.testing import FlaskClient
from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session

from backend.model.user import Role, User


def test_create_user_expected_json(
    test_client: FlaskClient,
    admin_session: None,
    create_user_payload: dict[str, str | bool],
) -> None:
    response = test_client.post('/users')
    assert response.status_code == 400
    assert response.json == {'message': 'expected_json'}

    payload = create_user_payload.copy()
    payload['not_email'] = 'not-an-email'
    response = test_client.post('/users', json=payload)
    assert response.status_code == 400
    assert response.json == {'not_email': ['Unknown field.']}


def test_create_user_success(
    test_client: FlaskClient,
    admin_session: None,
    monkeypatch: pytest.MonkeyPatch,
    create_user_payload: dict[str, str | bool],
) -> None:
    send_created_email = Mock()
    monkeypatch.setattr(User, 'send_created_email', send_created_email)

    response = test_client.post('/users', json=create_user_payload)

    assert response.status_code == 201
    data = cast(dict[str, str], response.get_json())
    assert data['id']
    send_created_email.assert_called_once()


def test_create_user_duplicate(
    test_client: FlaskClient,
    admin_session: None,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
    create_user_payload: dict[str, str | bool],
) -> None:
    monkeypatch.setattr(User, 'send_created_email', lambda self: None)
    payload = create_user_payload.copy()
    payload['email'] = user.email
    response = test_client.post('/users', json=payload)

    assert response.status_code == 409
    assert response.json == {'message': 'duplicate_user'}


def test_update_user(
    test_client: FlaskClient,
    admin_session: None,
    user: User,
) -> None:
    response = test_client.put(
        f'/users/{user.id}',
        json={'first_name': 'Updated'},
    )
    assert response.status_code == 200
    data = cast(dict[str, str], response.get_json())
    assert data['first_name'] == 'Updated'


def test_get_user(
    test_client: FlaskClient,
    admin_session: None,
    user: User,
) -> None:
    response = test_client.get(f'/users/{user.id}')
    assert response.status_code == 200
    user_data = cast(dict[str, str], response.get_json())
    assert user_data['id'] == str(user.id)


def test_list_users(
    test_client: FlaskClient,
    admin_session: None,
    user: User,
) -> None:
    response = test_client.get('/users')
    assert response.status_code == 200
    users_data = cast(dict[str, list[dict[str, str]]], response.get_json())
    assert any(u['id'] == str(user.id) for u in users_data['users'])


def test_delete_user(
    test_client: FlaskClient,
    admin_session: None,
    user: User,
) -> None:
    response = test_client.delete(f'/users/{user.id}')
    assert response.status_code == 204

    response = test_client.get(f'/users/{user.id}')
    assert response.status_code == 404
    assert response.get_json() == {'message': 'user_not_found'}


def test_send_created_email_endpoint(
    test_client: FlaskClient,
    admin_session: None,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
) -> None:
    send_email = Mock()
    monkeypatch.setattr('backend.model.user.Message.send', send_email)

    response = test_client.post(f'/users/{user.id}/send-created-email')
    assert response.status_code == 204
    send_email.assert_called_once()

    send_created_email = Mock()
    monkeypatch.setattr(user, 'send_created_email', send_created_email)

    response = test_client.post(f'/users/{user.id}/send-created-email')
    assert response.status_code == 204
    send_created_email.assert_called_once()


def test_get_password_state(
    test_client: FlaskClient,
    db_session: scoped_session[Session],
) -> None:
    response = test_client.get('/set-password/invalid-token')
    assert response.status_code == 404
    assert response.json == {'message': 'user_not_found'}

    user = User()
    user.email = 'password-state@example.com'
    user.first_name = 'Password'
    user.last_name = 'State'
    user.role = Role.USER
    user.password = None
    db_session.add(user)
    db_session.flush()

    response = test_client.get(f'/set-password/{user.get_password_token()}')
    assert response.status_code == 204

    user.set_password('already-set')
    db_session.flush()
    response = test_client.get(f'/set-password/{user.get_password_token()}')
    assert response.status_code == 409
    assert response.json == {'message': 'password_already_set'}


def test_set_password(
    test_client: FlaskClient,
    db_session: scoped_session[Session],
) -> None:
    response = test_client.post('/set-password/invalid-token', json={
        'password': 'new-password',
    })
    assert response.status_code == 404

    user = User()
    user.email = 'set-password@example.com'
    user.first_name = 'Set'
    user.last_name = 'Password'
    user.role = Role.USER
    user.password = None
    db_session.add(user)
    db_session.flush()

    token = user.get_password_token()
    response = test_client.post(f'/set-password/{token}', json={
        'password': 'new-password',
    })
    assert response.status_code == 204

    db_session.refresh(user)
    assert user.check_password('new-password')

    response = test_client.post(f'/set-password/{token}', json={
        'password': 'another-password',
    })
    assert response.status_code == 409
    assert response.json == {'message': 'password_already_set'}


def test_send_reset_password_email(
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
) -> None:
    response = test_client.get('/reset-password/missing@example.com')
    assert response.status_code == 404
    assert response.json == {'message': 'user_not_found'}

    send_email = Mock()
    monkeypatch.setattr('backend.model.user.Message.send', send_email)

    response = test_client.get(f'/reset-password/{user.email}')
    assert response.status_code == 204
    send_email.assert_called_once()

    send_reset_password_email = Mock()
    monkeypatch.setattr(
        user,
        'send_reset_password_email',
        send_reset_password_email,
    )

    response = test_client.get(f'/reset-password/{user.email}')
    assert response.status_code == 204
    send_reset_password_email.assert_called_once()


def test_reset_password(
    test_client: FlaskClient,
    user: User,
    user_password: str,
) -> None:
    response = test_client.post('/reset-password/invalid-token', json={
        'password': 'new-password',
    })
    assert response.status_code == 404

    token = user.get_password_token()
    response = test_client.post(f'/reset-password/{token}', json={
        'password': 'new-password',
    })
    assert response.status_code == 204
    assert user.check_password('new-password')
    assert not user.check_password(user_password)


def test_auth_user(
    test_client: FlaskClient,
    user: User,
    user_password: str,
) -> None:
    response = test_client.get('/auth', auth=(user.email, user_password))
    assert response.status_code == 200
    assert response.get_json() == {
        'id': str(user.id),
        'email': user.email,
        'role': Role.USER.value,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }


def test_none_password(
    user: User,
) -> None:
    user.password = None
    assert user.check_password('nope') is False
