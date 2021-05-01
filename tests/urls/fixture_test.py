import pytest

from app import ic
from app.auth import Group, UserMod
from tests.auth_test import VERIFIED_EMAIL_DEMO



@pytest.mark.fixtures
@pytest.mark.skip
def test_foo(loop, client, passwd):
    async def group_count():
        return await Group.all().count()
    
    async def get_user():
        return await UserMod.get_or_none(email=VERIFIED_EMAIL_DEMO).only('id')
        
    
    count = loop.run_until_complete(group_count())
    if not count:
        # Init
        res = client.get('/fixtures/init')
        data = res.json()
        assert data
        ic('SUCCESS: Groups and Permissions')
        
    usermod = loop.run_until_complete(get_user())
    if not usermod:
        # Users
        res = client.get('/fixtures/users')
        data = res.json()
        assert isinstance(data, dict)
        ic('SUCCESS: Users data created')
        userid = data.get("id")
        ic(userid)

        # Options
        res = client.get('/fixtures/options')
        data = res.json()
        assert data
        ic('SUCCESS: Options data created')

        # Login
        d = dict(username=VERIFIED_EMAIL_DEMO, password=passwd)
        res = client.post('/auth/login', data=d)
        data = res.json()
        ic(f'SUCCESS: Login completed.')
        access_token = data.get('access_token')
        ic(access_token)
    
