def test_create_and_get_books(client):
    response = client.post('/api/v1/books', json={
        'title': 'Test Book',
        'author': 'Author A',
        'isbn': '123456'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'book' in data
    book_id = data['book']['id']

    response = client.get('/api/v1/books')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['books']) == 1

    response = client.get(f'/api/v1/books/{book_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['book']['title'] == 'Test Book'

def test_update_book(client):
    response = client.post('/api/v1/books', json={
        'title': 'Old Title',
        'author': 'Author B',
        'isbn': '654321'
    })
    book_id = response.get_json()['book']['id']

    response = client.put(f'/api/v1/books/{book_id}', json={'title': 'New Title'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['book']['title'] == 'New Title'

def test_delete_book(client):
    response = client.post('/api/v1/books', json={
        'title': 'Delete Me',
        'author': 'Author C',
        'isbn': '111111'
    })
    book_id = response.get_json()['book']['id']

    response = client.delete(f'/api/v1/books/{book_id}')
    assert response.status_code == 200

    response = client.get(f'/api/v1/books/{book_id}')
    assert response.status_code == 404

def test_search_books(client):
    client.post('/api/v1/books', json={'title': 'Alice in Wonderland', 'author': 'Lewis', 'isbn': '222'})
    client.post('/api/v1/books', json={'title': 'Through the Looking Glass', 'author': 'Lewis', 'isbn': '333'})
    client.post('/api/v1/books', json={'title': 'Another Story', 'author': 'Someone', 'isbn': '444'})

    response = client.get('/api/v1/books/search?query=Alice')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['books']) == 1
    assert data['books'][0]['title'] == 'Alice in Wonderland'