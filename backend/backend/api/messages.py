from flask import abort, request

from . import api
from backend.model import Message, db


@api.get('/messages')
def messages_list():
    return {'messages': [
        message.to_dict()
        for message in Message.query.order_by(Message.id)
    ]}


@api.post('/messages')
def messages_post():
    json = request.json

    if 'text' not in json or not json['text']:
        abort(400, 'expected_text')

    db.session.add(Message(text=json['text']))
    db.session.commit()

    return '', 201
