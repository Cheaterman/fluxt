import uuid

from flask import abort, make_response
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.routing import BaseConverter

from backend.model import db


class Message(db.Model):  # type: ignore
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column()

    def to_dict(self) -> dict[str, str]:
        return {'text': self.text}


class MessageConverter(BaseConverter):
    def to_python(self, value: str) -> Message:
        message = db.session.get(Message, value)

        if not message:
            abort(make_response({'message': 'message_not_found'}, 404))

        return message
