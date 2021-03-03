import pytest, json
from app.demoroutes import ACCESS_TOKEN_DEMO
from app import ic      # noqa


VERIFIED_EMAIL_DEMO = 'enchance@gmail.com'
UNVERIFIED_EMAIL_DEMO = 'semi@amazon.co.uk'

PASSWORD_RESET_TOKEN_DEMO = ''
EMAIL_VERIFICATION_TOKEN_DEMO = ''


# @pytest.mark.focus
# @pytest.mark.skip
def test_register(client, random_email, passwd):
    # TODO: Must retry
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201
    
    # with pytest.raises(Exception):
    #     client.post('/auth/register', data=data)
    

@pytest.mark.focus
# @pytest.mark.skip
def test_login(client, passwd):
    if not VERIFIED_EMAIL_DEMO:
        assert False, 'Missing verified user email.'
    else:
        # TODO: Must retry
        d = dict(username=VERIFIED_EMAIL_DEMO, password=passwd)
        res = client.post('/auth/login', data=d)
        assert res.status_code == 200
        data = res.json()
        assert data.get('is_verified')
        assert data.get('token_type') == 'bearer'

    if not UNVERIFIED_EMAIL_DEMO:
        assert False, 'Missing unverified user email.'
    else:
        d = dict(username=UNVERIFIED_EMAIL_DEMO, password=passwd)
        res = client.post('/auth/login', data=d)
        assert res.status_code == 200
        data = res.json()
        # ic(data)
        assert data.get('is_verified') is False

    with pytest.raises(Exception):
        d = dict(username='aaa@bbb.com', password=passwd)
        res = client.post('/auth/login', data=d)


# @pytest.mark.focus
# @pytest.mark.skip
def test_logout(client):
    # TODO: Must retry
    if not ACCESS_TOKEN_DEMO:
        assert False, 'Missing token for logout.'
    else:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN_DEMO}'
        }
        res = client.post('/auth/logout', headers=headers)
        assert res.status_code == 200


# # @pytest.mark.focus
# @pytest.mark.skip
# def test_email_verification(client):
#     if not EMAIL_VERIFICATION_TOKEN_DEMO:
#         assert False, 'Missing email verification hash.'
#     else:
#         # TODO: Must retry
#         res = client.get(f'/auth/verify/{EMAIL_VERIFICATION_TOKEN_DEMO}')
#         data = res.json()
#         assert res.status_code == 200
#         assert data.get('success')


# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_change_password_after(client):
#     if not VERIFIED_EMAIL_DEMO:
#         assert False, 'Missing verified user email.'
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
#         assert False, 'Missing password change token.'
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