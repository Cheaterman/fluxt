import datetime
import uuid
from typing import TypedDict

from flask import abort, make_response
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.routing import BaseConverter

from backend.model import Model, db
from backend.model.user import User


class MessageInfo(TypedDict):
    id: str
    date: str
    author: str
    text: str


class Message(Model):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    author_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey(User.id))
    text: Mapped[str]

    author: Mapped[User | None] = relationship(User)


class MessageConverter(BaseConverter):
    def to_python(self, value: str) -> Message:
        message = db.session.get(Message, value)

        if not message:
            abort(make_response({'message': 'message_not_found'}, 404))

        return message
