from __future__ import annotations

import typing

from flask import current_app, session

from backend.api.auth import AuthInfo, RoleValue
from .user import Role


class Admin:
    @classmethod
    def auth(cls, email: str, password: str) -> Admin | None:
        if session.get('admin'):
            return cls()

        admin = cls.from_credentials(email, password)

        if admin:
            session['admin'] = True
            return admin

        return None

    def get_role(self) -> Role:
        return Role.ADMINISTRATOR

    def get_auth_info(self) -> AuthInfo:
        return {
            'id': '',
            'email': 'admin',
            'role': typing.cast(RoleValue, self.get_role().value),
        }

    @classmethod
    def from_credentials(cls, email: str, password: str) -> Admin | None:
        if (
            email == 'admin'
            and password == current_app.config['ADMIN_PASSWORD']
        ):
            return cls()

        return None
