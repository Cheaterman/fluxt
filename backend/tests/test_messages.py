import json

from flask.testing import FlaskClient

from backend.demo.model.message import Message


def test_messages_stream(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    response = test_client.get('/messages')
    assert response.status_code == 200
    response_iterator = response.iter_encoded()

    # Ignore existing messages
    for _ in Message.query:
        next(response_iterator)

    assert next(response_iterator) == b':heartbeat\n'
    response = test_client.post('/messages', json={'text': 'Some text'})
    message_id = response.get_json()['id']
    data = json.loads(next(response_iterator).decode()[len('data: '):])
    assert data['id'] == message_id
    assert data['text'] == 'Some text'


def test_messages_post_invalid(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    before_count = Message.query.count()

    response = test_client.post('/messages')
    assert response.status_code == 400
    assert response.json == {'message': 'expected_json'}
    assert Message.query.count() == before_count

    response = test_client.post('/messages', json={'not_text': 'Some text'})
    assert response.status_code == 400
    assert response.json == {'not_text': ['Unknown field.']}
    assert Message.query.count() == before_count


def test_messages_post_empty(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    before_count = Message.query.count()

    response = test_client.post('/messages', json={'text': ''})
    assert response.status_code == 400
    assert response.json == {'text': ['Shorter than minimum length 1.']}
    assert Message.query.count() == before_count


def test_messages_post_valid(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    before_count = Message.query.count()

    response = test_client.get('/messages')
    response_iterator = response.iter_encoded()

    # Ignore existing messages
    for _ in Message.query:
        next(response_iterator)

    response = test_client.post('/messages', json={'text': 'Some text'})
    assert Message.query.count() == before_count + 1
    last_message = Message.query.order_by(Message.date.desc()).first()
    assert last_message
    assert last_message.text == 'Some text'
    assert response.status_code == 201
    assert response.json == {'id': str(last_message.id)}

    assert next(response_iterator) == b':heartbeat\n'
    data = json.loads(next(response_iterator).decode()[len('data: '):])
    assert data['id'] == str(last_message.id)
    assert data['text'] == 'Some text'


def test_messages_delete_valid(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    before_count = Message.query.count()
    response = test_client.post('/messages', json={'text': 'Some text'})
    message_id = response.get_json()['id']
    assert Message.query.count() == before_count + 1

    response = test_client.delete(f'/messages/{message_id}')
    assert response.status_code == 204
    assert response.data == b''
    assert Message.query.count() == before_count
