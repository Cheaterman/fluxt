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
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.routing import BaseConverter

from . import db


class Role(enum.StrEnum):
    ADMINISTRATOR = enum.auto()
    USER = enum.auto()


class User(db.Model):  # type: ignore
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    _email: Mapped[str] = mapped_column('email', unique=True)
    password: Mapped[str] = mapped_column()
    role: Mapped[RoleValue] = mapped_column()

    @hybrid_property
    def email(self):
        return self._email

    @email.setter  # type: ignore[no-redef]
    def email(self, value: str):
        self._email = value.lower()

    @email.expression  # type: ignore[no-redef]
    def email(cls):  # pylint: disable=no-self-argument
        return func.lower(cls._email)

    @classmethod
    def auth(cls, email: str, password: str) -> User | None:
        user_id = session.get('user_id')

        if user_id:
            user = db.session.get(cls, user_id)
        else:
            user = cls.from_credentials(email, password)

        if user:
            session['user_id'] = user.id
            return user

        return None

    def get_role(self) -> Role:
        return Role(self.role)

    def get_auth_info(self) -> AuthInfo:
        return {
            'id': str(self.id),
            'email': self.email,
            'role': typing.cast(RoleValue, self.get_role().value),
        }

    @classmethod
    def from_email(cls, email: str) -> User | None:
        user: User | None = cls.query.filter_by(
            email=email.lower(),
        ).one_or_none()
        return user

    @classmethod
    def from_credentials(cls, email: str, password: str) -> User | None:
        user = cls.from_email(email.lower())

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
                cls.email == user.email,
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
