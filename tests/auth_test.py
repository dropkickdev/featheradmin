import pytest, json, redis
from pydantic import UUID4

from app import red, ic  # noqa
from app.cache import red
from app.auth.auth import current_user
from app.auth import UserMod, UserDB
from app.settings import settings as s
from limeutils.redis.models import StarterModel


VERIFIED_EMAIL_DEMO = 'enchance@gmail.com'
VERIFIED_USER_DEMO = 'f389fe8f-26e1-4cf4-93bd-e2ade152a6eb'
ACCESS_TOKEN_DEMO = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZjM4OWZlOGYtMjZlMS00Y2Y0LTkzYmQtZTJhZGUxNTJhNmViIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjQ4MzAwNjUxfQ.6wCa2pyNLwUPeZ6Dqsf-A16K4brFPM3TutJV9o1q8Ew'
UNVERIFIED_EMAIL_DEMO = 'unverified@gmail.com'

EMAIL_VERIFICATION_TOKEN_DEMO = ''
PASSWORD_RESET_TOKEN_DEMO = ''
EMAIL_VERIFICATION_TOKEN_EXPIRED = ''


@pytest.mark.register
# @pytest.mark.skip
def test_register(client, random_email, passwd):
    # Valid
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201
    
    # Exists
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    data = res.json()
    assert res.status_code == 400
    assert data.get('detail') == 'REGISTER_USER_ALREADY_EXISTS'

    # Not email
    data = json.dumps(dict(email='aaa', password=passwd))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 422

    # Empty
    data = json.dumps(dict(email='', password=passwd))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 422
    

@pytest.mark.login
# @pytest.mark.skip
def test_login(client, passwd):
    # Verified
    d = dict(username=VERIFIED_EMAIL_DEMO, password=passwd)
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    data = res.json()
    # ic(data)
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


# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_logout(client, headers):
#     res = client.post('/auth/logout', headers=headers)
#     ic(vars(res))
#     # assert res.status_code == 200


# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_email_verification_TOKEN_REQUIRED(client):     # noqa
#     if not EMAIL_VERIFICATION_TOKEN_DEMO:
#         assert True, 'Missing email verification token. Skipping test.'
#     else:
#         res = client.get(f'/auth/verify?t={EMAIL_VERIFICATION_TOKEN_DEMO}')
#         data = res.json()
#         assert res.status_code == 200, 'The token for verifying must have already been used.'
#         assert data.get('is_verified'), 'User dict was not returned after verifying email.'
#
#
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
#
#
# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_reset_password_request(client):
#     if not VERIFIED_EMAIL_DEMO:
#         assert True, 'Missing verified user email. Skipping test.'
#     else:
#         data = json.dumps(dict(email=VERIFIED_EMAIL_DEMO))
#         res = client.post('/auth/forgot-password', data=data)
#         assert res.status_code == 202
#
#
# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_reset_password_TOKEN_REQUIRED(client, passwd):     # noqa
#     if not PASSWORD_RESET_TOKEN_DEMO:
#         assert True, 'Missing password change token. Skipping test.'
#     else:
#         data = json.dumps(dict(token=PASSWORD_RESET_TOKEN_DEMO, password=passwd))
#         res = client.post('/auth/reset-password', data=data)
#         assert res.status_code == 200
#
#
# # @pytest.mark.demopages
# # @pytest.mark.skip
# def test_public_page(client):
#     res = client.get('/demo/public')
#     data = res.json()
#     # ic(data)
#     assert res.status_code == 200
#     assert data == 'public'
#
#
# # @pytest.mark.demopages
# # @pytest.mark.skip
# def test_private_page_auth(client, passwd):
#     d = dict(username=VERIFIED_EMAIL_DEMO, password=passwd)
#     res = client.post('/auth/login', data=d)
#     data = res.json()
#     access_token = data.get("access_token")
#     ic(access_token)
#
#     headers = {
#         'Authorization': f'Bearer {access_token}'
#     }
#     res = client.get('/demo/private', headers=headers)
#     data = res.json()
#     ic(data)
#     # assert res.status_code == 200
#     # assert data == 'private'
#
#
# # @pytest.mark.demopages
# # @pytest.mark.skip
# def test_private_page_noauth(client):
#     res = client.request('GET', '/demo/private')
#     data = res.json()
#     assert res.status_code == 401
#     assert data.get('detail') == 'Unauthorized'
#
#
# # @pytest.mark.focus
# @pytest.mark.skip
# def test_user_add_perm(client):
#     headers = {
#         'Authorization': f'Bearer {ACCESS_TOKEN_DEMO}'
#     }
#     res = client.post('/test/dev_user_add_perm', headers=headers)
#     data = res.json()
#     # ic(data)
#     assert data.get('id') == VERIFIED_USER_ID
#     assert data.get('email') == VERIFIED_EMAIL_DEMO
#
#
# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_token(client):
#     res = client.post('/test/dev_token')
#     data = res.json()
#     # ic(data)