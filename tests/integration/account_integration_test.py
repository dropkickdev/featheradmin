import pytest, json, jwt
from typing import Tuple
from fastapi_users.utils import generate_jwt
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import JWT_ALGORITHM
from tortoise.exceptions import OperationalError

from app import ic
from app.settings import settings as s
from app.auth import userdb, UserDBComplete, UserMod
from tests.auth_test import get_usermod, get_fapiuser_user



def register_user(client, random_email, passwd):
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    data = res.json()
    a = res.status_code == 201
    b = data.get('is_active')
    c = data.get('is_verified')
    if res.status_code == 201:
        assert a
        assert b
        assert not c
        return res, a, b, c
    return res, None

def verify_user(loop, client, id):
    user = loop.run_until_complete(get_fapiuser_user(id))
    a = user.is_verified
    b = user.is_active
    assert not a
    assert b
    
    if not a and b:
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "aud": VERIFY_USER_TOKEN_AUDIENCE,
        }
        token = generate_jwt(
            data=token_data,
            secret=s.SECRET_KEY_EMAIL,
            lifetime_seconds=s.VERIFY_EMAIL_TTL,
        )
        
        res = client.get(f'/auth/verify?t={token}&debug=true')
        decoded_token = jwt.decode(token, s.SECRET_KEY_EMAIL, audience=VERIFY_USER_TOKEN_AUDIENCE,
                                   algorithms=[JWT_ALGORITHM])
        data = res.json()
        usermod = loop.run_until_complete(get_usermod(decoded_token.get('user_id')))
        a = str(usermod.id) == data.get('id')
        b = usermod.email == data.get('email')
        c = usermod.is_verified
        assert a
        assert b
        assert c
        return a, b, c

def login(client, random_email, passwd):
    d = dict(username=random_email, password=passwd)
    res = client.post('/auth/login', data=d)
    data = res.json()
    
    if res.status_code == 200:
        data = res.json()
        access_token = data.get('access_token', None)
        a = data.get('is_verified')
        b = data.get('token_type') == 'bearer'
        assert access_token
        assert a
        assert b
        return access_token, a, b
    elif res.status_code == 400:
        a = data.get('detail') == 'LOGIN_BAD_CREDENTIALS'
        assert a
        return a
    else:
        ic('ERROR: login')

def logout(access_token, client):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    res = client.post('/auth/logout', headers=headers)
    data = res.json()
    a = res.status_code == 200
    b = data
    assert a
    assert b is None
    return a, b

def full_login(loop, client, random_email, passwd):
    """
    Generates a randomized user via Registration, Validation, and Login. Don't forget to call
    tempdb() first before using this in order to use the testing database.
    """
    async def ab():
        usermod = await UserMod.get_or_none(email=random_email).only(*userdb.select_fields)
        return UserDBComplete(**(await usermod.to_dict()))

    res, *_ = register_user(client, random_email, passwd)
    data = res.json()
    
    # Check in case random_email was already used
    if res.status_code == 201:
        _ = verify_user(loop, client, data.get('id'))
        access_token, *_ = login(client, random_email, passwd)
        return loop.run_until_complete(ab()), access_token
    
# @pytest.mark.focus
def test_auth_process(tempdb, client, loop, random_email, passwd):
    """
    Processes:
    Register, Login w/o verifying account, verify account, Login after verifying, Logout
    :return: None
    """
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())

    # 1. Register
    res, a, b, c = register_user(client, random_email, passwd)
    data = res.json()
    if a and b and not c:
        ic('Register: [PASS]')
    else:
        ic('Register: [FAIL]')

    # 2. Login 1: Unverified
    a = login(client, random_email, passwd)
    if a:
        ic('Unverified Login: [PASS]')
    else:
        ic('Unverified Login: [FAIL]')

    # 3. Verify user
    a, b, c = verify_user(loop, client, data.get('id'))
    if all([a, b, c]):
        ic('Verification: [PASS]')
    else:
        ic('Verification: [FAIL]')

    # 3. Login 2: Verified
    access_token, a, b = login(client, random_email, passwd)
    if all([a, b]):
        ic('Verified Login: [PASS]')
    else:
        ic('Verified Login: [FAIL]')

    # 4. Logout
    a, b = logout(access_token, client)
    if a and b is None:
        ic('Logout: [PASS]')
    else:
        ic('Logout: [FAIL]')

    # ic('Full Login...')
    # user = full_login(loop, client, random_email, passwd)
    # ic(user)
    
# @pytest.mark.focus
def test_full_login(tempdb, loop, client, random_email, passwd):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    user, access_token = full_login(loop, client, random_email, passwd)
    assert isinstance(user, UserDBComplete)
    assert isinstance(access_token, str)
