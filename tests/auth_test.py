import pytest, json
from app.demoroutes import ACCESS_TOKEN_DEMO
from app import ic      # noqa


VERIFIED_EMAIL_DEMO = 'enchance@gmail.com'
UNVERIFIED_EMAIL_DEMO = 'unverified@gmail.com'

PASSWORD_RESET_TOKEN_DEMO = ''
EMAIL_VERIFICATION_TOKEN_DEMO = ''
EMAIL_VERIFICATION_TOKEN_EXPIRED = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOWNlOTViYzgtZTJmZC00N2ZhLThmNmMtNjMwYzhjYTI5OWE5IiwiZW1haWwiOiJjb252ZXJzZXNAYW1hem9uLmNvbS5waCIsImF1ZCI6ImZhc3RhcGktdXNlcnM6dmVyaWZ5IiwiZXhwIjoxNjE0NzY0ODgyfQ.MHW1dAa9JLA4jmPTNQExmUVIlsGvBrkkLGmiBhrwIMc'


@pytest.mark.register
# @pytest.mark.skip
def test_register(client, random_email, passwd):
    # TODO: Must retry
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201
    
    res = client.post('/auth/register', data=data)
    assert res.status_code == 400
    

# @pytest.mark.focus
# @pytest.mark.skip
def test_login(client, passwd):
    if not VERIFIED_EMAIL_DEMO:
        assert True, 'Missing verified user email Skipping test.'
    else:
        # TODO: Must retry
        d = dict(username=VERIFIED_EMAIL_DEMO, password=passwd)
        res = client.post('/auth/login', data=d)
        assert res.status_code == 200
        data = res.json()
        assert data.get('is_verified')
        assert data.get('token_type') == 'bearer'

    if not UNVERIFIED_EMAIL_DEMO:
        assert True, 'Missing unverified user email Skipping test.'
    else:
        d = dict(username=UNVERIFIED_EMAIL_DEMO, password=passwd)
        res = client.post('/auth/login', data=d)
        data = res.json()
        assert res.status_code == 400
        assert data.get('detail') == 'LOGIN_BAD_CREDENTIALS'
    

# @pytest.mark.focus
def test_login_unknown_user(client, passwd):
    d = dict(username='aaa@bbb.com', password=passwd)
    res = client.post('/auth/login', data=d)
    data = res.json()
    assert res.status_code == 400
    assert data.get('detail') == 'LOGIN_BAD_CREDENTIALS'


# @pytest.mark.focus
# @pytest.mark.skip
def test_logout(client):
    # TODO: Must retry
    if not ACCESS_TOKEN_DEMO:
        assert True, 'Missing token for logout. Skipping test.'
    else:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN_DEMO}'
        }
        res = client.post('/auth/logout', headers=headers)
        assert res.status_code == 200


# @pytest.mark.focus
# @pytest.mark.skip
def test_email_verification(client):
    if not EMAIL_VERIFICATION_TOKEN_DEMO:
        assert True, 'Missing email verification token. Skipping test.'
    else:
        # TODO: Must retry
        res = client.get(f'/auth/verify?token={EMAIL_VERIFICATION_TOKEN_DEMO}')
        data = res.json()
        assert res.status_code == 200
        assert data.get('is_verified'), 'User dict was not returned after verifying email.'


# @pytest.mark.focus
# @pytest.mark.skip
def test_email_verification_expired(client):
    if not EMAIL_VERIFICATION_TOKEN_EXPIRED:
        assert True, 'Missing expired email verification token. Skipping test.'
    else:
        # TODO: Must retry
        res = client.get(f'/auth/verify?token={EMAIL_VERIFICATION_TOKEN_EXPIRED}')
        data = res.json()
        assert res.status_code == 400
        assert data.get('detail') == 'VERIFY_USER_TOKEN_EXPIRED'


# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_change_password_after(client):
#     if not VERIFIED_EMAIL_DEMO:
#         assert True, 'Missing verified user email Skipping test.'
#     else:
#         data = json.dumps(dict(email=VERIFIED_EMAIL_DEMO))
#         res = client.post('/auth/forgot-password', data=data)
#         success = res.json()
#         assert success
#         assert res.status_code == 202
#
# # @pytest.mark.focus
# @pytest.mark.skip
# def test_reset_password_after(client):
#     if not PASSWORD_RESET_TOKEN_DEMO:
#         assert True, 'Missing password change token Skipping test.'
#     else:
#         password = 'pass123'
#         data = json.dumps(dict(token=PASSWORD_RESET_TOKEN_DEMO, password=password))
#         res = client.post('/auth/reset-password', data=data)
#         ic(res)
#         success = res.json
#         assert success
#         assert res.status_code == 200


# # @pytest.mark.skip
# @pytest.mark.demopages
# def test_open_public_page(client):
#     res = client.get('/demo/public')
#     data = res.json()
#     assert res.status_code == 200
#     assert data == 'public'
#
#
# # @pytest.mark.skip
# @pytest.mark.demopages
# def test_open_private_page(client):
#     headers = {
#         'Authorization': f'Bearer {ACCESS_TOKEN_DEMO}'
#     }
#     res = client.request('GET','/demo/private', headers=headers)
#     data = res.json()
#     assert res.status_code == 200
#     assert data == 'private'