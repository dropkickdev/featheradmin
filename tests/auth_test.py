import json


def test_register(client, random_email, ic):
    data = json.dumps(dict(email=random_email, password='pass123'))
    try:
        res = client.post('/auth/register', data=data)
        assert res.status_code == 201
        ic(random_email)
    except Exception as e:
        ic(e)