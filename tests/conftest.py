import pytest, random
from tortoise import Tortoise
from fastapi.testclient import TestClient
from fastapi_users.utils import generate_jwt
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import JWT_ALGORITHM

from main import get_app
from fixtures.routes import init, create_users, create_options
from app import ic
from app.settings import settings as s
from app.auth import UserMod
from app.settings.db import DATABASE_MODELS, DATABASE_URL
from .auth_test import ACCESS_TOKEN_DEMO, VERIFIED_ID_DEMO




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
def random_int(minimum: int = 0, maximum: int = 120):
    return random.randint(minimum, maximum)

@pytest.fixture
def random_email(random_word):
    host = random.choice(['gmail', 'yahoo', 'amazon', 'yahoo', 'microsoft', 'google'])
    tld = random.choice(['org', 'com', 'net', 'io', 'com.ph', 'co.uk'])
    return f'{random_word}@{host}.{tld}'


@pytest.fixture
def passwd():
    return 'pass123'


@pytest.fixture
def headers():
    return {
        'Authorization': f'Bearer {ACCESS_TOKEN_DEMO}'
    }


@pytest.fixture
def auth_headers(tempdb, loop):
    async def ab():
        return await tempdb()
    user = loop.run_until_complete(ab())
    
    token_data = {
        "user_id": str(user.id),
        "email": user.email,
        "aud": 'fastapi-users:auth',
    }
    access_token = generate_jwt(
        data=token_data,
        secret=s.SECRET_KEY,
        lifetime_seconds=s.ACCESS_TOKEN_EXPIRE,
    )
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    yield headers, user

@pytest.fixture
async def db():
    """Sauce: https://github.com/tortoise/tortoise-orm/issues/99"""
    await Tortoise.init(db_url=DATABASE_URL, modules={'models': DATABASE_MODELS})
    await Tortoise.generate_schemas()

@pytest.fixture
def fixtures():
    async def ab():
        await init()
        user = await create_users()
        await create_options()
        return user
    yield ab

@pytest.fixture
def tempdb(fixtures):
    async def tempdb():
        await Tortoise.init(db_url="sqlite://:memory:", modules={"models": DATABASE_MODELS})
        await Tortoise.generate_schemas()
        return await fixtures()
    yield tempdb

@pytest.fixture
def loop(client):
    yield client.task.get_loop()

# @pytest.fixture
# def user(loop):
#     async def ab():
#         return await user_data(VERIFIED_USER_DEMO)
#     return loop.run_until_complete(ab())

# This is a pytest hook. It works but we're not using it.
# func_of_interest = "test_get_and_cache"
# def pytest_runtest_teardown(item, nextitem):
#     curr_name = item.function.__qualname__
#     # check to see it is the function we want
#     if curr_name == func_of_interest:
#         # check to see if there are any more functions after this one
#         if nextitem is not None:
#             next_name = nextitem.function.__qualname__
#         else:
#             next_name = "random_name"
#         # check to see if the next item is a different function
#         if curr_name != next_name:
#             print("Perform some teardown once")