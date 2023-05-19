from backend.model import Message


def test_messages_list(client):
    response = client.get('/messages')
    assert response.status_code == 200
    data = response.json
    assert 'messages' in data
    assert len(data['messages']) == Message.query.count()
    messages = {
        'messages': [
            {'text': message.text}
            for message in Message.query.order_by(Message.id)
        ]
    }
    assert data == messages


def test_messages_post_invalid(client):
    before_count = Message.query.count()

    response = client.post('/messages')
    assert response.status_code == 400
    assert response.json == {'message': 'expected_json'}
    assert Message.query.count() == before_count

    response = client.post('/messages', json={'not_text': 'Some text'})
    assert response.status_code == 400
    assert response.json == {'message': 'expected_text'}
    assert Message.query.count() == before_count


def test_messages_post_empty(client):
    before_count = Message.query.count()

    response = client.post('/messages', json={'text': ''})
    assert response.status_code == 400
    assert response.json == {'message': 'expected_text'}
    assert Message.query.count() == before_count


def test_messages_post_valid(client):
    before_count = Message.query.count()

    response = client.post('/messages', json={'text': 'Some text'})
    assert response.status_code == 201
    assert response.data == b''
    assert Message.query.count() == before_count + 1
    last_message = Message.query.order_by(Message.id.desc()).first()
    assert last_message.text == 'Some text'

    data = client.get('/messages').json
    assert data['messages'][-1]['text'] == 'Some text'
