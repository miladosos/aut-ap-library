def test_create_and_get_users(client):
    response = client.post('/api/v1/users', json={
        'username': 'testuser',
        'name': 'Test User',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'user' in data
    user_id = data['user']['id']

    response = client.get('/api/v1/users')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['users']) == 1

    response = client.get(f'/api/v1/users/{user_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['username'] == 'testuser'

def test_update_user(client):
    response = client.post('/api/v1/users', json={
        'username': 'olduser',
        'name': 'Old Name',
        'email': 'old@example.com'
    })
    user_id = response.get_json()['user']['id']

    response = client.put(f'/api/v1/users/{user_id}', json={'name': 'New Name'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['name'] == 'New Name'

def test_delete_user(client):
    response = client.post('/api/v1/users', json={
        'username': 'deleteuser',
        'name': 'Delete Me',
        'email': 'delete@example.com'
    })
    user_id = response.get_json()['user']['id']

    response = client.delete(f'/api/v1/users/{user_id}')
    assert response.status_code == 200

    response = client.get(f'/api/v1/users/{user_id}')
    assert response.status_code == 404