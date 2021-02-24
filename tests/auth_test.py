import pytest, json
from app import ic      # noqa


VERIFIED_EMAIL = 'enchance@gmail.com'
UNVERIFIED_EMAIL = 'semi@amazon.co.uk'

ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYzZmNzEyNDItZGE4NC00MTY0LWE5NGQtOTZlMDZlMGY4OTI0IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjQ1NzA4NTI5fQ.V968cJj_5M41odgdzm1ZgM-XpxWZ88YDKgiOPdzBE2c'
PASSWORD_RESET_TOKEN = ''
EMAIL_VERIFICATION_TOKEN = ''


# @pytest.mark.focus
# @pytest.mark.skip
def test_register(client, random_email, passwd):
    # TODO: Must retry
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201
    
    with pytest.raises(Exception):
        client.post('/auth/register', data=data)

@pytest.mark.focus
# @pytest.mark.skip
def test_login(client, passwd):
    if not VERIFIED_EMAIL:
        assert False, 'Missing verified user email.'
    else:
        # TODO: Must retry
        d = dict(username=VERIFIED_EMAIL, password=passwd)
        res = client.post('/auth/login', data=d)
        assert res.status_code == 200
        data = res.json()
        assert data.get('is_verified')
        assert data.get('token_type') == 'bearer'

    if not UNVERIFIED_EMAIL:
        assert False, 'Missing unverified user email.'
    else:
        d = dict(username=UNVERIFIED_EMAIL, password=passwd)
        res = client.post('/auth/login', data=d)
        assert res.status_code == 200
        data = res.json()
        assert data.get('is_verified') is False
        assert data.get('token_type') is None
    
    
    with pytest.raises(Exception):
        d = dict(username='aaa@bbb.com', password=passwd)
        client.post('/auth/login', data=d)

# @pytest.mark.focus
# @pytest.mark.skip
def test_logout(client):
    # TODO: Must retry
    if not ACCESS_TOKEN:
        assert False, 'Missing token for logout.'
    else:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}'
        }
        res = client.get('/auth/logout', headers=headers)
        assert res.status_code == 200
        
    
# @pytest.mark.focus
@pytest.mark.skip
def test_email_verification(client):
    if not EMAIL_VERIFICATION_TOKEN:
        assert False, 'Missing email verification hash.'
    else:
        # TODO: Must retry
        res = client.get(f'/auth/verify/{EMAIL_VERIFICATION_TOKEN}')
        data = res.json()
        assert res.status_code == 200
        assert data.get('success')
        

# @pytest.mark.focus
# @pytest.mark.skip
def test_change_password_after(client):
    if not VERIFIED_EMAIL:
        assert False, 'Missing verified user email.'
    else:
        data = json.dumps(dict(email=VERIFIED_EMAIL))
        res = client.post('/auth/forgot-password', data=data)
        success = res.json()
        assert success
        assert res.status_code == 202

# @pytest.mark.focus
@pytest.mark.skip
def test_reset_password_after(client):
    if not PASSWORD_RESET_TOKEN:
        assert False, 'Missing password change token.'
    else:
        password = 'pass123'
        data = json.dumps(dict(token=PASSWORD_RESET_TOKEN, password=password))
        res = client.post('/auth/reset-password', data=data)
        ic(res)
        success = res.json
        assert success
        assert res.status_code == 200
