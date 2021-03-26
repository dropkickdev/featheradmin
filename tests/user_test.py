import pytest, redis

from app import ic
from app.auth import current_user
from app.cache import red
from .auth_test import VERIFIED_USER_ID, VERIFIED_EMAIL_DEMO, ACCESS_TOKEN_DEMO


@pytest.mark.focus
# @pytest.mark.skip
def test_current_user_data(client, passwd, headers):
    res = client.post('/test/dev_user_data', headers=headers)
    data = res.json()
    ic(data)
    # assert data.get('id') == VERIFIED_USER_ID
    # assert data.get('email') == VERIFIED_EMAIL_DEMO


# # @pytest.mark.focus
# @pytest.mark.skip
# def test_add_perm(client, headers):
#     res = client.post('/test/dev_user_add_perm', headers=headers)
#     data = res.json()
#     # ic(data)
#     assert data.get('id') == VERIFIED_USER_ID
#     assert data.get('email') == VERIFIED_EMAIL_DEMO
#     assert data.get('groups'), 'User needs to have at least one (1) group'
#     # assert data.get('permissions'), 'User needs to have at least one (1) permission'
#     # assert data.get('options'), 'User needs to have at least one (1) option'
#
#
# # @pytest.mark.focus
# @pytest.mark.skip
# def test_add_group(client, headers):
#     res = client.post('/test/dev_user_add_group', headers=headers)
#     data = res.json()
#     # ic(data)
#     assert data.get('id') == VERIFIED_USER_ID
#     assert data.get('email') == VERIFIED_EMAIL_DEMO
#     assert data.get('groups'), 'User needs to have at least one (1) group'
#     assert data.get('permissions'), 'User needs to have at least one (1) permission'
#     assert data.get('options'), 'User needs to have at least one (1) option'
#
#
# # @pytest.mark.focus
# @pytest.mark.skip
# def test_has_perm(client, headers):
#     res = client.post('/test/dev_has_permission', headers=headers)
#     data = res.json()
#     # ic(data)
#
#
# def test_has_group(client):
#     group = 'AccountGroup'
#
#
# def test_has_groups(client):
#     pass

