from flask import abort, request

from . import api, auth
from backend.model import Message, db


@api.get('/messages')
def messages_list():
    return {'messages': [
        message.to_dict()
        for message in Message.query.order_by(Message.id)
    ]}


@api.post('/messages')
def messages_add():
    json = request.json

    if not json.get('text'):
        abort(400, 'expected_text')

    db.session.add(Message(text=json['text']))
    db.session.commit()

    return '', 201


@api.delete('/messages/<int:id>')
@auth.login_required
def messages_delete(id):
    message = db.session.get(Message, id)

    if not message:
        abort(404, 'invalid_message_id')

    db.session.delete(message)
    db.session.commit()

    return '', 204
