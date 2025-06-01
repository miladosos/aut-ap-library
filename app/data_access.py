import os
import redis

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
r = redis.from_url(redis_url, decode_responses=True)

def get_next_book_id():
    return str(r.incr('next_book_id'))

def add_book(book_data):
    book_id = get_next_book_id()
    book_key = f"book:{book_id}"
    book_data.update({
        'id': book_id,
        'is_reserved': 'false',
        'reserved_by': ''
    })
    r.hset(book_key, mapping=book_data)
    r.sadd('books', book_id)
    return get_book_by_id(book_id)

def get_all_books():
    book_ids = r.smembers('books') or set()
    books = []
    for bid in book_ids:
        book = r.hgetall(f"book:{bid}")
        if book:
            book['is_reserved'] = book['is_reserved'] == 'true'
            books.append(book)
    return books

def get_book_by_id(book_id):
    book = r.hgetall(f"book:{book_id}")
    if not book:
        return None
    book['is_reserved'] = book['is_reserved'] == 'true'
    return book

def update_book(book_id, updates):
    book_key = f"book:{book_id}"
    if not r.exists(book_key):
        return None
    if 'title' in updates:
        r.hset(book_key, 'title', updates['title'])
    if 'author' in updates:
        r.hset(book_key, 'author', updates['author'])
    if 'isbn' in updates:
        r.hset(book_key, 'isbn', updates['isbn'])
    return get_book_by_id(book_id)

def delete_book(book_id):
    book_key = f"book:{book_id}"
    book = get_book_by_id(book_id)
    if not book:
        return False, 'not_found'
    if book['is_reserved']:
        return False, 'reserved'
    r.delete(book_key)
    r.srem('books', book_id)
    return True, None

def search_books(query):
    book_ids = r.smembers('books') or set()
    results = []
    for bid in book_ids:
        book = r.hgetall(f"book:{bid}")
        if book and query.lower() in book.get('title', '').lower():
            book['is_reserved'] = book['is_reserved'] == 'true'
            results.append(book)
    return results

def get_next_user_id():
    return str(r.incr('next_user_id'))

def add_user(user_data):
    user_id = get_next_user_id()
    user_key = f"user:{user_id}"
    user_data.update({'id': user_id})
    r.hset(user_key, mapping=user_data)
    r.sadd('users', user_id)
    return get_user_by_id(user_id)

def get_all_users():
    user_ids = r.smembers('users') or set()
    users = []
    for uid in user_ids:
        user = r.hgetall(f"user:{uid}")
        if user:
            users.append(user)
    return users

def get_user_by_id(user_id):
    user = r.hgetall(f"user:{user_id}")
    if not user:
        return None
    return user

def update_user(user_id, updates):
    user_key = f"user:{user_id}"
    if not r.exists(user_key):
        return None
    if 'username' in updates:
        r.hset(user_key, 'username', updates['username'])
    if 'name' in updates:
        r.hset(user_key, 'name', updates['name'])
    if 'email' in updates:
        r.hset(user_key, 'email', updates['email'])
    return get_user_by_id(user_id)

def delete_user(user_id):
    user_key = f"user:{user_id}"
    user = get_user_by_id(user_id)
    if not user:
        return False, 'not_found'
    reserved_books = r.smembers(f"user:{user_id}:reserved_books") or set()
    if reserved_books:
        return False, 'has_reservations'
    r.delete(user_key)
    r.srem('users', user_id)
    return True, None

def reserve_book(book_id, user_id):
    book = get_book_by_id(book_id)
    if not book:
        return False, 'book_not_found'
    user = get_user_by_id(user_id)
    if not user:
        return False, 'user_not_found'
    if book['is_reserved']:
        return False, 'already_reserved'
    book_key = f"book:{book_id}"
    r.hset(book_key, 'is_reserved', 'true')
    r.hset(book_key, 'reserved_by', user_id)
    r.sadd(f"user:{user_id}:reserved_books", book_id)
    reservation_id = f"{user_id}:{book_id}"
    return True, reservation_id

def unreserve_book(book_id, user_id):
    book = get_book_by_id(book_id)
    if not book:
        return False, 'book_not_found'
    user = get_user_by_id(user_id)
    if not user:
        return False, 'user_not_found'
    if not book['is_reserved'] or book['reserved_by'] != user_id:
        return False, 'not_reserved_by_user'
    book_key = f"book:{book_id}"
    r.hset(book_key, 'is_reserved', 'false')
    r.hset(book_key, 'reserved_by', '')
    r.srem(f"user:{user_id}:reserved_books", book_id)
    return True, None

def get_user_reservations(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return None, 'user_not_found'
    reserved_book_ids = r.smembers(f"user:{user_id}:reserved_books") or set()
    books = []
    for bid in reserved_book_ids:
        book = get_book_by_id(bid)
        if book:
            books.append(book)
    return books, None