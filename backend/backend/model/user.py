from __future__ import annotations
import enum
import typing
import uuid

import bcrypt
from flask import (
    abort,
    current_app,
    make_response,
    session,
)
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.routing import BaseConverter

from . import db


class Role(enum.StrEnum):
    ADMINISTRATOR = enum.auto()
    USER = enum.auto()


class User(db.Model):  # type: ignore
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column()

    @classmethod
    def auth(cls, name: str, password: str) -> User | None:
        user_id = session.get('user_id')

        if user_id:
            user = db.session.get(cls, user_id)
        else:
            user = cls.from_credentials(name, password)

        if user:
            session['user_id'] = user.id
            return user

        return None

    def get_roles(self) -> list[Role]:
        return [Role(self.role)]

    def get_auth_info(self) -> AuthInfo:
        return {
            'id': str(self.id),
            'name': self.name,
            'roles': [
                typing.cast(RoleValue, role.value)
                for role in self.get_roles()
            ],
        }

    @classmethod
    def from_credentials(cls, name: str, password: str) -> User | None:
        user: User | None = cls.query.filter_by(name=name).one_or_none()

        if user and user.check_password(password):
            return user

        return None

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf8'),
            self.password.encode('utf8'),
        )

    @classmethod
    def check_duplicate(cls, user: User) -> None:
        with db.session.no_autoflush:
            count = cls.query.filter(
                cls.id != user.id,
                cls.name == user.name,
            ).count()

        if count:
            abort(409, 'duplicate_user')

    def set_password(self, password: str) -> None:
        self.password = bcrypt.hashpw(
            password.encode('utf8'),
            bcrypt.gensalt(rounds=4 if current_app.config['TESTING'] else 12)
        ).decode('utf8')


class UserConverter(BaseConverter):
    def to_python(self, value: str) -> User:
        user = db.session.get(User, value)

        if not user:
            abort(make_response({'message': 'user_not_found'}, 404))

        return user


from backend.api.auth import AuthInfo, RoleValue  # noqa: E402
