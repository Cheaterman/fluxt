from flask import abort, request
from flask.typing import ResponseReturnValue

from backend.model import db
from backend.model.message import Message
from . import api
from .auth import auth


@api.get('/messages')
def messages_list() -> ResponseReturnValue:
    return {'messages': [
        message.to_dict()
        for message in Message.query.order_by(Message.id)
    ]}


@api.post('/messages')
def messages_add() -> ResponseReturnValue:
    json = request.get_json()

    if not json.get('text'):
        abort(400, 'expected_text')

    db.session.add(Message(text=json['text']))
    db.session.commit()

    return '', 201


@api.delete('/messages/<message:message>')
@auth.login_required
def messages_delete(message: Message) -> ResponseReturnValue:
    db.session.delete(message)
    db.session.commit()

    return '', 204
