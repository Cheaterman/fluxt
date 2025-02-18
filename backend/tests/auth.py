import typing

import pytest
from flask.testing import FlaskClient

from backend.model.user import Role, User

SESSIONS = {
    Role.ADMINISTRATOR: 'admin_session',
    Role.USER: 'user_session',
}


@pytest.fixture
def admin_session(test_client: FlaskClient) -> None:
    with test_client.session_transaction() as session:
        session['admin'] = True


@pytest.fixture
def user_session(
    test_client: FlaskClient,
    user: User,
    user_password: str,  # pylint: disable=unused-argument
) -> None:
    with test_client.session_transaction() as session:
        session['user_id'] = user.id


@pytest.fixture(params=[None] + list(
    Role._member_map_.values()  # pylint: disable=no-member,protected-access
))
def role(request: pytest.FixtureRequest) -> Role | None:
    _role = typing.cast(Role, request.param)
    fixture = SESSIONS.get(_role)

    if fixture is None:
        return None

    request.getfixturevalue(fixture)
    return _role
