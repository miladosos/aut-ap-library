def test_reserve_and_unreserve_book(client):
    user_resp = client.post('/api/v1/users', json={
        'username': 'resuser',
        'name': 'Res User',
        'email': 'res@example.com'
    })
    user_id = user_resp.get_json()['user']['id']

    book_resp = client.post('/api/v1/books', json={
        'title': 'Res Book',
        'author': 'Author R',
        'isbn': '777'
    })
    book_id = book_resp.get_json()['book']['id']

    response = client.post(
        f'/api/v1/books/{book_id}/reserve',
        json={'user_id': user_id}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'reservation_id' in data

    response = client.delete(f'/api/v1/books/{book_id}')
    assert response.status_code == 400

    response = client.post(
        f'/api/v1/users/{user_id}/reservations',
        json={'user_id': user_id}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id'] == book_id

    response = client.post(
        f'/api/v1/books/{book_id}/unreserve',
        json={'user_id': user_id}
    )
    assert response.status_code == 200

    response = client.post(
        f'/api/v1/users/{user_id}/reservations',
        json={'user_id': user_id}
    )
    data = response.get_json()
    assert data == []
