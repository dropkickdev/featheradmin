import pytest, json
from app import ic      # noqa



def test_register(client, random_email, passwd):
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201
    
    with pytest.raises(Exception):
        client.post('/auth/register', data=data)
        

# @pytest.mark.skip
# @pytest.mark.focus
def test_login(client, passwd):
    d = dict(username='inclinations@amazon.net', password=passwd)
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    data = res.json()
    assert data.get('is_verified')
    assert data.get('token_type') == 'bearer'
    
    d = dict(username='translates@yahoo.io', password=passwd)
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    data = res.json()
    assert data.get('is_verified') is False
    assert data.get('token_type') is None
    
    with pytest.raises(Exception):
        d = dict(username='aaa@bbb.com', password=passwd)
        client.post('/auth/login', data=d)

@pytest.mark.skip
# @pytest.mark.focus
def test_logout(client):
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMzhhYTRiOTktMTAyNi00ZDVjLThiN2QtN2FhZDVjYjI3ODAwIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjEyMTkyNzE2fQ.fOWP_hh1VZJ1VEB11E4m21fwwE-f9pw3O-bE9MSM9yw'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    res = client.get('/auth/logout', headers=headers)
    assert res.status_code == 200