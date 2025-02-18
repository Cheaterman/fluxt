from flask.testing import FlaskClient

from backend.model.message import Message


def test_messages_list(test_client: FlaskClient) -> None:
    response = test_client.get('/messages')
    assert response.status_code == 200
    data = response.json
    assert data
    assert len(data['messages']) == Message.query.count()
    messages = {
        'messages': [
            {'text': message.text}
            for message in Message.query.order_by(Message.id)
        ]
    }
    assert data == messages


def test_messages_post_invalid(test_client: FlaskClient) -> None:
    before_count = Message.query.count()

    response = test_client.post('/messages')
    assert response.status_code == 400
    assert response.json == {'message': 'expected_json'}
    assert Message.query.count() == before_count

    response = test_client.post('/messages', json={'not_text': 'Some text'})
    assert response.status_code == 400
    assert response.json == {'message': 'expected_text'}
    assert Message.query.count() == before_count


def test_messages_post_empty(test_client: FlaskClient) -> None:
    before_count = Message.query.count()

    response = test_client.post('/messages', json={'text': ''})
    assert response.status_code == 400
    assert response.json == {'message': 'expected_text'}
    assert Message.query.count() == before_count


def test_messages_post_valid(test_client: FlaskClient) -> None:
    before_count = Message.query.count()

    response = test_client.post('/messages', json={'text': 'Some text'})
    assert response.status_code == 201
    assert response.data == b''
    assert Message.query.count() == before_count + 1
    last_message = Message.query.order_by(Message.id.desc()).first()
    assert last_message.text == 'Some text'

    data = test_client.get('/messages').json
    assert data
    assert data['messages'][-1]['text'] == 'Some text'
