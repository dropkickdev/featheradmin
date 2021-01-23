import pytest, json
from app import ic      # noqa


def test_register(client, random_email):
    data = json.dumps(dict(email=random_email, password='pass123'))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201

# @pytest.mark.skip
# @pytest.mark.focus
def test_login(client):
    d = dict(username='syllogisms@amazon.co.uk', password='pass123')
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    data = res.json()
    assert data.get('is_verified')
    assert data.get('token_type') == 'bearer'
    
    d = dict(username='fewest@amazon.co.uk', password='pass123')
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    data = res.json()
    assert not data.get('is_verified')
    
    with pytest.raises(Exception):
        d = dict(username='aaa@bbb.com', password='pass123')
        client.post('/auth/login', data=d)

# @pytest.mark.skip
# @pytest.mark.focus
def test_logout(client):
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiNDBiNTIzOGUtNDMyNy00NDVlLTg4NDUtYWQzMDk2OTI5MjQ3IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjExNDg5MzYwfQ.p0FIbC33Alhpi50OT_mLZ9dXYnWF5hQ3hufjrfHDdAo'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    res = client.get('/auth/logout', headers=headers)
    assert res.status_code == 200