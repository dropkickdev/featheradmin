import pytest

from app import ic
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
    ic(data)
    assert data.get('id') == VERIFIED_USER_ID
    assert data.get('email') == VERIFIED_EMAIL_DEMO
    
    
@pytest.mark.skip
def test_has_perm(client):
    # Check all perms from groups and user
    pass

@pytest.mark.focus
def test_add_group(client, headers):
    res = client.post('/test/dev_user_add_group', headers=headers)
    data = res.json()
    # ic(data)


def test_has_group(client):
    group = 'AccountGroup'


def test_has_groups(client):
    pass
