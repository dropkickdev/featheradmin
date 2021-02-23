import pytest, json
from app import ic      # noqa


verify_hash = None

@pytest.mark.focus
def test_register(client, random_email, passwd):
    # TODO: Must retry
    data = json.dumps(dict(email=random_email, password=passwd))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201
    
    with pytest.raises(Exception):
        client.post('/auth/register', data=data)
        
def test_login(client, passwd):
    # TODO: Must retry
    d = dict(username='enchance@gmail.com', password=passwd)
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    data = res.json()
    assert data.get('is_verified')
    assert data.get('token_type') == 'bearer'
    
    d = dict(username='semi@amazon.co.uk', password=passwd)
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    data = res.json()
    assert data.get('is_verified') is False
    assert data.get('token_type') is None
    
    with pytest.raises(Exception):
        d = dict(username='aaa@bbb.com', password=passwd)
        client.post('/auth/login', data=d)

# @pytest.mark.focus
@pytest.mark.skip
def test_logout(client):
    # TODO: Must retry
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYzZmNzEyNDItZGE4NC00MTY0LWE5NGQtOTZlMDZlMGY4OTI0IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjE0MTUyMDk1fQ.6r8_xZ9HqGfxGTc3xEApq7YWI9uhSBn6gwcISLaYS8I'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    res = client.get('/auth/logout', headers=headers)
    assert res.status_code == 200
    
@pytest.mark.verifyemail
@pytest.mark.skip
def test_verify(client):
    # TODO: Must retry
    res = client.get(
        '/auth/verify/7c05322e0f4f9aeca126076bcfa2ee43875d39b4da5b236552c582cf66820655')
    data = res.json()
    assert res.status_code == 200
    assert data.get('success')


def test_change_password(client):
    pass

