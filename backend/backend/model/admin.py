from __future__ import annotations

import typing

from flask import current_app, session

from backend.api.auth import AuthInfo, RoleValue
from .user import Role


class Admin:
    @classmethod
    def auth(cls, username: str, password: str) -> Admin | None:
        if session.get('admin'):
            return cls()

        admin = cls.from_credentials(username, password)

        if admin:
            session['admin'] = True
            return admin

        return None

    def get_roles(self) -> list[Role]:
        return [Role.ADMINISTRATOR]

    def get_auth_info(self) -> AuthInfo:
        return {
            'id': '',
            'name': 'admin',
            'roles': [
                typing.cast(RoleValue, role.value)
                for role in self.get_roles()
            ],
        }

    @classmethod
    def from_credentials(cls, username: str, password: str) -> Admin | None:
        if (
            username == 'admin'
            and password == current_app.config['ADMIN_PASSWORD']
        ):
            return cls()

        return None
