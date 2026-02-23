from __future__ import annotations

from typing import Self

from flask import current_app, session

from .user import Role


class SuperAdmin:
    email = 'admin'
    first_name = 'Admin'
    last_name = ''

    @classmethod
    def auth(cls, username: str, password: str) -> Self | None:
        if session.get('admin'):
            return cls()

        admin: Self | None = cls.from_credentials(username, password)

        if admin:
            session['admin'] = True
            return admin

        return None

    def get_role(self) -> Role:
        return Role.ADMINISTRATOR

    def get_auth_info(self) -> AuthInfo:
        return {
            'id': '',
            'email': self.email,
            'role': self.get_role(),
            'first_name': self.first_name,
            'last_name': self.last_name,
        }

    @classmethod
    def from_credentials(cls, username: str, password: str) -> Self | None:
        if (
            username == cls.email
            and password == current_app.config['ADMIN_PASSWORD']
        ):
            return cls()

        return None


from backend.api.auth import AuthInfo  # noqa: E402
