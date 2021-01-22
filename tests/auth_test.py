import pytest, json
from app import ic


def test_register(client, random_email):
    data = json.dumps(dict(email=random_email, password='pass123'))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201

# @pytest.mark.skip
# @pytest.mark.focus
def test_login_existent(client):
    d = dict(username='protective@yahoo.co.uk', password='pass123')
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    # try:
    # except Exception as e:
    #     ic(type(e))
    #     raise e

@pytest.mark.focus
def test_login_nonexistent(client):
    d = dict(username='aaa@bbb.com', password='pass123')
    with pytest.raises(AttributeError):
        client.post('/auth/login', data=d)
