import pytest
import redis
import os
from app.application import app

@pytest.fixture(scope='session')
def redis_client():
    url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    r = redis.from_url(url, decode_responses=True)
    r.flushdb()
    return r

@pytest.fixture
def client(redis_client):
    redis_client.flushdb()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client