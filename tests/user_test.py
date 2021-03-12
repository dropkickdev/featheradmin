import pytest, redis

from app import ic, redconn
from .auth_test import VERIFIED_USER_ID, VERIFIED_EMAIL_DEMO, ACCESS_TOKEN_DEMO


# @pytest.mark.focus
# @pytest.mark.skip
def test_current_user_data(client, passwd):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN_DEMO}'
    }
    res = client.post('/test/dev_view_user_data', headers=headers)
    data = res.json()
    # ic(data)
    assert data.get('id') == VERIFIED_USER_ID
    assert data.get('email') == VERIFIED_EMAIL_DEMO


# @pytest.mark.focus
# @pytest.mark.skip
def test_add_perm(client, headers):
    res = client.post('/test/dev_user_add_perm', headers=headers)
    data = res.json()
    # ic(data)
    assert data.get('id') == VERIFIED_USER_ID
    assert data.get('email') == VERIFIED_EMAIL_DEMO


# @pytest.mark.focus
def test_add_group(client, headers):
    res = client.post('/test/dev_user_add_group', headers=headers)
    data = res.json()
    # ic(data)
    assert data.get('id') == VERIFIED_USER_ID
    assert data.get('email') == VERIFIED_EMAIL_DEMO
    
@pytest.mark.skip
def test_has_perm(client):
    # Check all perms from groups and user
    pass


def test_has_group(client):
    group = 'AccountGroup'


def test_has_groups(client):
    pass


# @pytest.mark.focus
def test_redis_conn():
    ret = redconn.set('hey', 'fam')
    assert ret
    ret = redconn.get('hey')
    assert ret == 'fam'
    ret = redconn.get('meh', 'bam')
    assert ret == 'bam'
    assert isinstance(redconn.conn, redis.Redis)
    # ic(ret)
