import pytest, json
from app import ic


def test_register(client, random_email):
    data = json.dumps(dict(email=random_email, password='pass123'))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201

# @pytest.mark.skip
@pytest.mark.focus
def test_login(client):
    d = dict(username='protective@yahoo.co.uk', password='pass123')
    res = client.post('/auth/login', data=d)
    assert res.status_code == 200
    # try:
    # except Exception as e:
    #     ic(type(e))
    #     raise e
