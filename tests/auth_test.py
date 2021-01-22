import pytest, json


def test_register(client, random_email, ic):
    data = json.dumps(dict(email=random_email, password='pass123'))
    res = client.post('/auth/register', data=data)
    assert res.status_code == 201
    # ic(random_email)


@pytest.mark.focus
def test_login(client, ic):
    try:
        data = json.dumps(dict(email='enchance@gmail.com', password='pass123'))
        res = client.post('/auth/login', data=data)
        assert res.status_code == 200
        # ic(res)
    except Exception as e:
        ic(type(e))
        raise e
