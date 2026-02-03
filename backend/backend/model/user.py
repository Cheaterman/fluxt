from __future__ import annotations

import datetime
import enum
import uuid
from typing import Self

import bcrypt
from flask import (
    abort,
    current_app,
    make_response,
    render_template,
    session,
    url_for,
)
from flask_emails import Message  # type: ignore[import-untyped]
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy import Function, func, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.routing import BaseConverter

from backend import nuxtify
from . import Model, db


class Role(enum.StrEnum):
    ADMINISTRATOR = enum.auto()
    USER = enum.auto()


class User(Model):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )
    _email: Mapped[str] = mapped_column('email', unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    password: Mapped[str | None]
    role: Mapped[Role]
    enabled: Mapped[bool] = mapped_column(server_default=text('TRUE'))

    files: Mapped[list[File]] = relationship(back_populates='author')

    @hybrid_property
    def email(self) -> str:
        return self._email

    @email.setter
    def email_setter(self, value: str) -> None:
        self._email = value.lower()

    @email.expression
    def email_expression(cls) -> Function[str]:
        return func.lower(cls._email)

    @classmethod
    def auth(cls, email: str, password: str) -> Self | None:
        user_id = session.get('user_id')

        if user_id:
            user = db.session.get(cls, user_id)
        else:
            user = cls.from_credentials(email, password)

        if user and user.enabled:
            session['user_id'] = user.id
            return user

        return None

    def get_role(self) -> Role:
        return Role(self.role)

    def get_auth_info(self) -> AuthInfo:
        return {
            'id': str(self.id),
            'email': self.email,
            'role': self.get_role(),
            'first_name': self.first_name,
            'last_name': self.last_name,
        }

    @classmethod
    def from_email(cls, email: str) -> Self | None:
        user: Self | None = cls.query.filter_by(
            email=email.lower(),
        ).one_or_none()
        return user

    @classmethod
    def from_credentials(cls, email: str, password: str) -> Self | None:
        user = cls.from_email(email.lower())

        if user and user.check_password(password):
            return user

        return None

    def check_password(self, password: str) -> bool:
        if not self.password:
            return False

        return bcrypt.checkpw(
            password.encode('utf8'),
            self.password.encode('utf8'),
        )

    @classmethod
    def check_duplicate(cls, user: Self) -> None:
        with db.session.no_autoflush:
            count = cls.query.filter(
                cls.id != user.id,
                cls.email == user.email,
            ).count()

        if count:
            abort(409, 'duplicate_user')

    @classmethod
    def get_password_tokenizer(cls) -> URLSafeSerializer:
        return URLSafeSerializer(
            current_app.config['SECRET_KEY'],
            salt='password',
        )

    def get_password_token(self) -> str:
        token = self.get_password_tokenizer().dumps({'id': str(self.id)})
        assert isinstance(token, str)
        return token

    @classmethod
    def from_password_token(cls, token: str) -> User | None:
        try:
            data = cls.get_password_tokenizer().loads(token)
        except BadSignature:
            return None

        return db.session.get(cls, data['id'])

    def set_password(self, password: str) -> None:
        self.password = bcrypt.hashpw(
            password.encode('utf8'),
            bcrypt.gensalt(rounds=4 if current_app.config['TESTING'] else 12)
        ).decode('utf8')

    def send_created_email(self) -> None:
        url = nuxtify(url_for(
            'api.get_password_state',
            token=self.get_password_token(),
            _external=True,
        ))

        email = Message(
            subject='Account creation',
            html=render_template(
                'email_user_created.html',
                user=self,
                url=url,
            ),
            mail_from=('Fluxt', current_app.config['EMAIL_HOST_USER']),
        )
        email.send(to=self.email)

    def send_reset_password_email(self) -> None:
        url = nuxtify(url_for(
            'api.reset_password',
            token=self.get_password_token(),
            _external=True,
        ))

        email = Message(
            subject='Password reset',
            html=render_template(
                'email_reset_password.html',
                user=self,
                url=url,
            ),
            mail_from=('Fluxt', current_app.config['EMAIL_HOST_USER']),
        )
        email.send(to=self.email)


class UserConverter(BaseConverter):
    def to_python(self, value: str) -> User:
        user = db.session.get(User, value)

        if not user:
            abort(make_response({'message': 'user_not_found'}, 404))

        return user


from backend.api.auth import AuthInfo  # noqa: E402
from .file import File  # noqa: E402
