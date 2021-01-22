import pytest, random
from fastapi.testclient import TestClient

from main import get_app


@pytest.fixture
def client():
    with TestClient(get_app()) as tc:
        yield tc

@pytest.fixture
def random_word():
    """For linux only"""
    with open('/usr/share/dict/cracklib-small', 'r') as w:
        words = w.read().splitlines()
    return random.choice(words)

@pytest.fixture
def random_int(min: int = 0, max: int = 120):
    return random.randint(min, max)

@pytest.fixture
def random_email(random_word):
    host = random.choice(['gmail', 'yahoo', 'amazon', 'yahoo', 'microsoft', 'google'])
    tld = random.choice(['org', 'com', 'net', 'io', 'com.ph', 'co.uk'])
    return f'{random_word}@{host}.{tld}'