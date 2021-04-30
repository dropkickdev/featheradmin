import pytest, json, secrets, jwt
from fastapi_users.utils import generate_jwt
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import JWT_ALGORITHM

from app import red, ic  # noqa
from app.auth import UserMod, fapiuser, UserDB
from app.auth.routes import ResetPasswordPy
from app.settings import settings as s


VERIFIED_EMAIL_DEMO = 'enchance@gmail.com'
VERIFIED_ID_DEMO = '8cb607b3-ea0f-46ca-bca1-7d8e13293195'
ACCESS_TOKEN_DEMO = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOGNiNjA3YjMtZWEwZi00NmNhLWJjYTEtN2Q4ZTEzMjkzMTk1IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjUxMTQzNjkzfQ.-cJMW0HC-16fgDOSt4At7JzALOvoxIYx4iquXe4WxnY'
UNVERIFIED_EMAIL_DEMO = 'unverified@gmail.com'

EMAIL_VERIFICATION_TOKEN_DEMO = ''
PASSWORD_RESET_TOKEN_DEMO = ''
EMAIL_VERIFICATION_TOKEN_EXPIRED = ''


# def login_func(d, client):
#     data = dict(username=VERIFIED_EMAIL_DEMO, password=passwd)
#     res = client.post('/auth/login', data=data)
#     return res.json().get('access_token')

async def get_usermod(id):
    return await UserMod.get_or_none(pk=id).only('id', 'email', 'is_verified')


async def get_fapiuser_user(id):
    usermod = await get_usermod(id)
    if not usermod:
        return
    return await fapiuser.get_user(usermod.email)


@pytest.mark.register
def test_register(tempdb, client, loop, random_email, passwd):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    # Valid
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    data = res.json()
    # ic(data)
    assert res.status_code == 201
    assert data.get('is_active')
    assert not data.get('is_verified')

    # Exists
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    data = res.json()
    # ic(data)
    assert res.status_code == 400
    assert data.get('detail') == 'REGISTER_USER_ALREADY_EXISTS'

    # Not email
    data = json.dumps(dict(email='aaa', password=passwd))
    res = client.post('/auth/register', data=data)
    data = res.json()
    # ic(data)
    assert res.status_code == 422
    assert data.get('detail')[0].get('msg') == 'value is not a valid email address'

    # Empty
    data = json.dumps(dict(email='', password=passwd))
    res = client.post('/auth/register', data=data)
    data = res.json()
    # ic(data)
    assert res.status_code == 422
    assert data.get('detail')[0].get('msg') == 'value is not a valid email address'


# @pytest.mark.focus
def test_registration_verification(tempdb, loop, client, random_email, passwd):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    # Register
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    data = res.json()
    assert res.status_code == 201
    assert data.get('is_active')
    assert not data.get('is_verified')

    user = loop.run_until_complete(get_fapiuser_user(data.get('id')))
    if not user.is_verified and user.is_active:
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
        data = res.json()

        decoded_token = jwt.decode(token, s.SECRET_KEY_EMAIL, audience=VERIFY_USER_TOKEN_AUDIENCE,
                          algorithms=[JWT_ALGORITHM])
        usermod = loop.run_until_complete(get_usermod(decoded_token.get('user_id')))
        assert str(usermod.id) == data.get('id')
        assert usermod.email == data.get('email')
        assert usermod.is_verified


@pytest.mark.login
def test_login(tempdb, loop, client, passwd):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    # Verified
    d = dict(username=VERIFIED_EMAIL_DEMO, password=passwd)
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    data = res.json()
    ic(data)
    assert data.get('access_token')
    assert data.get('is_verified')
    assert data.get('token_type') == 'bearer'

    # Unverified
    d = dict(username=UNVERIFIED_EMAIL_DEMO, password=passwd)
    res = client.post('/auth/login', data=d)
    data = res.json()
    # ic(data)
    assert res.status_code == 400
    assert data.get('detail') == 'LOGIN_BAD_CREDENTIALS'

    # Uknown user
    d = dict(username='aaa@bbb.com', password=passwd)
    res = client.post('/auth/login', data=d)
    data = res.json()
    # ic(data)
    assert res.status_code == 400
    assert data.get('detail') == 'LOGIN_BAD_CREDENTIALS'


# @pytest.mark.focus
def test_logout(tempdb, loop, client, headers):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    res = client.post('/auth/logout', headers=headers)
    data = res.json()
    # ic(data)
    assert res.status_code == 200
    assert data


# @pytest.mark.focus
def test_reset_password_request(tempdb, loop, client):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())

    # Get the token to send alongside the password change form
    data = json.dumps(dict(email=VERIFIED_EMAIL_DEMO, debug=True))
    res = client.post('/auth/forgot-password', data=data)
    token = res.json()
    assert res.status_code == 202

    if token:
        # Password change form sent
        new_password = 'foobar'
        data = json.dumps(dict(token=token, password=new_password))
        res = client.post('/auth/reset-password', data=data)
        data = res.json()
        # ic(data)
        assert res.status_code == 200
        assert data

        # Verified
        # Test the change in password
        d = dict(username=VERIFIED_EMAIL_DEMO, password=new_password)
        res = client.post('/auth/login', data=d)
        assert res.status_code == 200
        data = res.json()
        # ic(data)
        assert data.get('access_token')
        assert data.get('is_verified')
        assert data.get('token_type') == 'bearer'


# @pytest.mark.focus
# def test_email_verification_TOKEN_REQUIRED(client):     # noqa
#     res = client.get(f'/auth/verify?t={EMAIL_VERIFICATION_TOKEN_DEMO}')
#     data = res.json()
#     assert res.status_code == 200, 'The token for verifying must have already been used.'
#     assert data.get('is_verified'), 'User dict was not returned after verifying email.'



# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_email_verification_expired(client):
#     if not EMAIL_VERIFICATION_TOKEN_EXPIRED:
#         assert True, 'Missing expired email verification token. Skipping test.'
#     else:
#         res = client.get(f'/auth/verify?t={EMAIL_VERIFICATION_TOKEN_EXPIRED}')
#         data = res.json()
#         assert res.status_code == 400
#         assert data.get('detail') == 'VERIFY_USER_TOKEN_EXPIRED'





# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_reset_password_TOKEN_REQUIRED(client, passwd):     # noqa
#     if not PASSWORD_RESET_TOKEN_DEMO:
#         assert True, 'Missing password change token. Skipping test.'
#     else:
#         data = json.dumps(dict(token=PASSWORD_RESET_TOKEN_DEMO, password=passwd))
#         res = client.post('/auth/reset-password', data=data)
#         assert res.status_code == 200





# @pytest.mark.focus
# # @pytest.mark.skip
# def test_user_add_perm(client, headers):
#     res = client.post('/test/dev_user_add_perm', headers=headers)
#     data = res.json()
#     ic(data)
#     assert data.get('id') == VERIFIED_USER_DEMO
#     assert data.get('email') == VERIFIED_EMAIL_DEMO
#
# 
# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_token(client):
#     res = client.post('/test/dev_token')
#     data = res.json()
#     # ic(data)



@pytest.mark.demopages
# @pytest.mark.skip
def test_public_page(client):
    res = client.get('/demo/public')
    data = res.json()
    # ic(data)
    assert res.status_code == 200
    assert data == 'public'

@pytest.mark.demopages
# @pytest.mark.skip
def test_private_page_auth(client, passwd, headers):
    res = client.get('/demo/private', headers=headers)
    data = res.json()
    # ic(data)
    assert res.status_code == 200
    assert data == 'private'

@pytest.mark.demopages
# @pytest.mark.skip
def test_private_page_noauth(client):
    res = client.request('GET', '/demo/private')
    data = res.json()
    # ic(data)
    assert res.status_code == 401
    assert data.get('detail') == 'Unauthorized'